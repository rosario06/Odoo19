# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import base64
import logging

_logger = logging.getLogger(__name__)


class EcfCertificate(models.Model):
    _name = 'ecf.certificate'
    _description = 'Certificados Digitales e-CF'
    _order = 'expiration_date desc'

    name = fields.Char(
        string='Nombre del Certificado',
        required=True
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company
    )
    
    certificate_file = fields.Binary(
        string='Archivo Certificado (.p12/.pfx)',
        required=True,
        attachment=True
    )
    
    certificate_filename = fields.Char(
        string='Nombre del Archivo'
    )
    
    password = fields.Char(
        string='Contraseña',
        required=True
    )
    
    # Información del certificado
    issuer = fields.Char(
        string='Emisor',
        readonly=True
    )
    
    subject = fields.Char(
        string='Sujeto',
        readonly=True
    )
    
    serial_number = fields.Char(
        string='Número de Serie',
        readonly=True
    )
    
    issue_date = fields.Date(
        string='Fecha de Emisión',
        readonly=True
    )
    
    expiration_date = fields.Date(
        string='Fecha de Expiración',
        readonly=True
    )
    
    is_expired = fields.Boolean(
        string='Expirado',
        compute='_compute_is_expired',
        store=True
    )
    
    days_to_expire = fields.Integer(
        string='Días para Expirar',
        compute='_compute_days_to_expire'
    )
    
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('validated', 'Validado'),
        ('active', 'Activo'),
        ('expired', 'Expirado'),
        ('revoked', 'Revocado'),
    ], string='Estado', default='draft', required=True)
    
    active = fields.Boolean(
        string='Activo',
        default=True
    )
    
    notes = fields.Text(
        string='Notas'
    )

    @api.depends('expiration_date')
    def _compute_is_expired(self):
        today = fields.Date.today()
        for record in self:
            record.is_expired = record.expiration_date and record.expiration_date < today

    @api.depends('expiration_date')
    def _compute_days_to_expire(self):
        today = fields.Date.today()
        for record in self:
            if record.expiration_date:
                delta = record.expiration_date - today
                record.days_to_expire = delta.days
            else:
                record.days_to_expire = 0

    def action_validate_certificate(self):
        """Valida el certificado y extrae su información"""
        self.ensure_one()
        
        if not self.certificate_file or not self.password:
            raise UserError(_('Debe cargar un certificado y proporcionar la contraseña.'))
        
        try:
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives.serialization import pkcs12
            from cryptography import x509
            
            # Decodificar el certificado
            cert_data = base64.b64decode(self.certificate_file)
            
            # Cargar el PKCS12
            private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
                cert_data,
                self.password.encode('utf-8'),
                backend=default_backend()
            )
            
            if not certificate:
                raise UserError(_('No se pudo cargar el certificado. Verifique la contraseña.'))
            
            # Extraer información del certificado
            issuer = certificate.issuer.rfc4514_string()
            subject = certificate.subject.rfc4514_string()
            serial = str(certificate.serial_number)
            not_valid_before = certificate.not_valid_before_utc
            not_valid_after = certificate.not_valid_after_utc
            
            self.write({
                'issuer': issuer,
                'subject': subject,
                'serial_number': serial,
                'issue_date': not_valid_before.date(),
                'expiration_date': not_valid_after.date(),
                'state': 'validated',
            })
            
            self._check_expiration_warnings()
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Certificado Validado'),
                    'message': _('El certificado es válido.\nExpira: %s') % not_valid_after.date(),
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            _logger.error(f'Error validando certificado {self.name}: {str(e)}')
            raise UserError(_('Error al validar el certificado: %s') % str(e))

    def action_set_active(self):
        """Establece este certificado como activo para la compañía"""
        self.ensure_one()
        
        if self.state != 'validated':
            raise UserError(_('Debe validar el certificado antes de activarlo.'))
        
        if self.is_expired:
            raise UserError(_('No puede activar un certificado expirado.'))
        
        # Desactivar otros certificados de la misma compañía
        self.search([
            ('company_id', '=', self.company_id.id),
            ('state', '=', 'active'),
            ('id', '!=', self.id)
        ]).write({'state': 'validated'})
        
        self.write({'state': 'active'})
        
        # Actualizar la compañía
        self.company_id.write({
            'l10n_do_ecf_certificate': self.certificate_file,
            'l10n_do_ecf_certificate_password': self.password,
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Certificado Activado'),
                'message': _('El certificado se ha activado correctamente.'),
                'type': 'success',
                'sticky': False,
            }
        }

    def _check_expiration_warnings(self):
        """Verifica y notifica sobre certificados próximos a expirar"""
        if self.days_to_expire <= 30 and self.days_to_expire > 0:
            _logger.warning(f'El certificado {self.name} expirará en {self.days_to_expire} días')
            
            # Crear actividad para el administrador
            self.activity_schedule(
                'mail.mail_activity_data_warning',
                summary=_('Certificado próximo a expirar'),
                note=_('El certificado %s expirará en %s días. Por favor, renuévelo.') % (self.name, self.days_to_expire),
                user_id=self.env.ref('base.user_admin').id
            )

    @api.model
    def _cron_check_certificates(self):
        """Cron para verificar certificados expirados"""
        certificates = self.search([
            ('state', 'in', ['validated', 'active']),
            ('expiration_date', '<=', fields.Date.today())
        ])
        
        for cert in certificates:
            cert.write({'state': 'expired', 'active': False})
            _logger.warning(f'Certificado {cert.name} marcado como expirado')

