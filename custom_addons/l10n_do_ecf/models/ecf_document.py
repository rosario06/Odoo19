# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import logging
import base64
import json

_logger = logging.getLogger(__name__)


class EcfDocument(models.Model):
    _name = 'ecf.document'
    _description = 'Documento de Facturación Electrónica DGII'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    # Información básica
    name = fields.Char(
        string='Número de Documento',
        required=True,
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
        index=True
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        readonly=True,
        default=lambda self: self.env.company
    )
    
    invoice_id = fields.Many2one(
        'account.move',
        string='Factura',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        ondelete='cascade',
        index=True
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente/Proveedor',
        related='invoice_id.partner_id',
        store=True,
        readonly=True
    )
    
    # Información fiscal
    ncf = fields.Char(
        string='NCF',
        related='invoice_id.l10n_latam_document_number',
        store=True,
        readonly=True
    )
    
    ecf_number = fields.Char(
        string='e-NCF',
        help='Número de e-CF asignado por DGII',
        readonly=True,
        copy=False,
        tracking=True
    )
    
    document_type = fields.Selection([
        ('31', 'e-Factura de Crédito Fiscal'),
        ('32', 'e-Factura de Consumo'),
        ('33', 'e-Nota de Débito'),
        ('34', 'e-Nota de Crédito'),
        ('43', 'e-Factura de Gastos Menores'),
        ('44', 'e-Factura de Regímenes Especiales'),
        ('45', 'e-Factura Gubernamental'),
        ('46', 'e-Factura de Exportación'),
        ('47', 'e-Factura para Pagos al Exterior'),
    ], string='Tipo de e-CF', required=True, readonly=True, states={'draft': [('readonly', False)]})
    
    # Fechas
    date = fields.Datetime(
        string='Fecha de Emisión',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=fields.Datetime.now
    )
    
    sent_date = fields.Datetime(
        string='Fecha de Envío',
        readonly=True,
        copy=False,
        tracking=True
    )
    
    approved_date = fields.Datetime(
        string='Fecha de Aprobación',
        readonly=True,
        copy=False,
        tracking=True
    )
    
    # Estado
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('to_send', 'Por Enviar'),
        ('sending', 'Enviando'),
        ('sent', 'Enviado'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
        ('cancelled', 'Anulado'),
        ('error', 'Error'),
    ], string='Estado', default='draft', required=True, tracking=True, copy=False)
    
    # XML
    xml_content = fields.Text(
        string='Contenido XML',
        readonly=True,
        copy=False
    )
    
    xml_signed = fields.Binary(
        string='XML Firmado',
        readonly=True,
        copy=False,
        attachment=True
    )
    
    xml_signed_filename = fields.Char(
        string='Nombre archivo XML',
        compute='_compute_xml_signed_filename'
    )
    
    # Respuestas DGII
    acuse_recibo = fields.Text(
        string='Acuse de Recibo',
        readonly=True,
        copy=False
    )
    
    aprobacion_comercial = fields.Text(
        string='Aprobación Comercial',
        readonly=True,
        copy=False
    )
    
    track_id = fields.Char(
        string='Track ID DGII',
        readonly=True,
        copy=False,
        help='Identificador de seguimiento asignado por DGII'
    )
    
    security_code = fields.Char(
        string='Código de Seguridad',
        readonly=True,
        copy=False,
        help='Código de seguridad generado por DGII'
    )
    
    qr_code = fields.Binary(
        string='Código QR',
        readonly=True,
        copy=False,
        attachment=True
    )
    
    # Errores
    error_message = fields.Text(
        string='Mensaje de Error',
        readonly=True,
        copy=False
    )
    
    error_code = fields.Char(
        string='Código de Error',
        readonly=True,
        copy=False
    )
    
    retry_count = fields.Integer(
        string='Intentos de Reenvío',
        default=0,
        readonly=True,
        copy=False
    )
    
    # Anulación
    cancellation_reason = fields.Text(
        string='Razón de Anulación',
        readonly=True,
        copy=False
    )
    
    cancellation_date = fields.Datetime(
        string='Fecha de Anulación',
        readonly=True,
        copy=False
    )
    
    # Metadatos
    log_ids = fields.One2many(
        'ecf.document.log',
        'document_id',
        string='Historial',
        readonly=True
    )

    @api.depends('ecf_number', 'ncf')
    def _compute_xml_signed_filename(self):
        for record in self:
            number = record.ecf_number or record.ncf or record.name
            record.xml_signed_filename = f'{number}_signed.xml'

    def action_generate_xml(self):
        """Genera el XML del e-CF según especificaciones DGII"""
        self.ensure_one()
        
        if not self.company_id.l10n_do_ecf_enabled:
            raise UserError(_('La facturación electrónica no está habilitada para esta compañía.'))
        
        try:
            # Generar XML usando el servicio
            xml_content = self.env['ecf.webservice'].generate_ecf_xml(self)
            
            self.write({
                'xml_content': xml_content,
                'state': 'to_send',
            })
            
            self._log_event('xml_generated', _('XML generado correctamente'))
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('XML Generado'),
                    'message': _('El XML del e-CF se ha generado correctamente.'),
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            _logger.error(f'Error generando XML para e-CF {self.name}: {str(e)}')
            self.write({
                'state': 'error',
                'error_message': str(e),
            })
            raise UserError(_('Error al generar XML: %s') % str(e))

    def action_sign_xml(self):
        """Firma digitalmente el XML con el certificado de la compañía"""
        self.ensure_one()
        
        if not self.xml_content:
            raise UserError(_('Debe generar el XML antes de firmarlo.'))
        
        if not self.company_id.l10n_do_ecf_certificate:
            raise UserError(_('No se ha configurado un certificado digital para esta compañía.'))
        
        try:
            # Firmar XML usando el servicio
            xml_signed = self.env['ecf.webservice'].sign_xml(
                self.xml_content,
                self.company_id.l10n_do_ecf_certificate,
                self.company_id.l10n_do_ecf_certificate_password
            )
            
            self.write({
                'xml_signed': base64.b64encode(xml_signed.encode('utf-8')),
            })
            
            self._log_event('xml_signed', _('XML firmado correctamente'))
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('XML Firmado'),
                    'message': _('El XML se ha firmado digitalmente.'),
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            _logger.error(f'Error firmando XML para e-CF {self.name}: {str(e)}')
            self.write({
                'state': 'error',
                'error_message': str(e),
            })
            raise UserError(_('Error al firmar XML: %s') % str(e))

    def action_send_to_dgii(self):
        """Envía el e-CF a DGII"""
        self.ensure_one()
        
        if not self.xml_signed:
            raise UserError(_('Debe firmar el XML antes de enviarlo a DGII.'))
        
        if self.state not in ['to_send', 'error']:
            raise UserError(_('El documento no está en estado para ser enviado.'))
        
        try:
            self.write({'state': 'sending'})
            
            # Enviar a DGII usando el servicio
            response = self.env['ecf.webservice'].send_to_dgii(self)
            
            self.write({
                'state': 'sent',
                'sent_date': fields.Datetime.now(),
                'track_id': response.get('track_id'),
                'acuse_recibo': json.dumps(response, indent=2),
            })
            
            self._log_event('sent_to_dgii', _('e-CF enviado a DGII correctamente'))
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Enviado a DGII'),
                    'message': _('El e-CF se ha enviado correctamente a DGII. Track ID: %s') % response.get('track_id'),
                    'type': 'success',
                    'sticky': True,
                }
            }
            
        except Exception as e:
            _logger.error(f'Error enviando e-CF {self.name} a DGII: {str(e)}')
            self.write({
                'state': 'error',
                'error_message': str(e),
                'retry_count': self.retry_count + 1,
            })
            raise UserError(_('Error al enviar a DGII: %s') % str(e))

    def action_check_status(self):
        """Consulta el estado del e-CF en DGII"""
        self.ensure_one()
        
        if not self.track_id:
            raise UserError(_('No hay Track ID para consultar el estado.'))
        
        try:
            # Consultar estado en DGII
            response = self.env['ecf.webservice'].check_status(self.track_id)
            
            status = response.get('status')
            
            if status == 'approved':
                self.write({
                    'state': 'approved',
                    'approved_date': fields.Datetime.now(),
                    'ecf_number': response.get('ecf_number'),
                    'security_code': response.get('security_code'),
                    'aprobacion_comercial': json.dumps(response, indent=2),
                })
                
                # Generar código QR
                self._generate_qr_code()
                
                self._log_event('approved', _('e-CF aprobado por DGII'))
                
                message = _('El e-CF ha sido APROBADO por DGII.\ne-NCF: %s') % response.get('ecf_number')
                notification_type = 'success'
                
            elif status == 'rejected':
                self.write({
                    'state': 'rejected',
                    'error_code': response.get('error_code'),
                    'error_message': response.get('error_message'),
                })
                
                self._log_event('rejected', _('e-CF rechazado por DGII'))
                
                message = _('El e-CF ha sido RECHAZADO por DGII.\nRazón: %s') % response.get('error_message')
                notification_type = 'danger'
                
            else:
                message = _('Estado actual: %s') % status
                notification_type = 'info'
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Estado e-CF'),
                    'message': message,
                    'type': notification_type,
                    'sticky': True,
                }
            }
            
        except Exception as e:
            _logger.error(f'Error consultando estado e-CF {self.name}: {str(e)}')
            raise UserError(_('Error al consultar estado: %s') % str(e))

    def action_cancel_ecf(self):
        """Anula el e-CF en DGII"""
        self.ensure_one()
        
        if self.state != 'approved':
            raise UserError(_('Solo se pueden anular e-CF aprobados.'))
        
        return {
            'name': _('Anular e-CF'),
            'type': 'ir.actions.act_window',
            'res_model': 'ecf.cancel.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_document_id': self.id}
        }

    def _generate_qr_code(self):
        """Genera el código QR para el e-CF"""
        try:
            import qrcode
            from io import BytesIO
            
            # Datos del QR según DGII
            qr_data = f"{self.company_id.vat}|{self.ecf_number}|{self.date}|{self.invoice_id.amount_total}|{self.security_code}"
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            qr_code_data = base64.b64encode(buffer.getvalue())
            
            self.write({'qr_code': qr_code_data})
            
        except Exception as e:
            _logger.warning(f'Error generando QR code para e-CF {self.name}: {str(e)}')

    def _log_event(self, event_type, message):
        """Registra un evento en el historial"""
        self.env['ecf.document.log'].create({
            'document_id': self.id,
            'event_type': event_type,
            'message': message,
            'date': fields.Datetime.now(),
        })


class EcfDocumentLog(models.Model):
    _name = 'ecf.document.log'
    _description = 'Historial de Documentos e-CF'
    _order = 'date desc'

    document_id = fields.Many2one(
        'ecf.document',
        string='Documento',
        required=True,
        ondelete='cascade',
        index=True
    )
    
    event_type = fields.Char(
        string='Tipo de Evento',
        required=True
    )
    
    message = fields.Text(
        string='Mensaje',
        required=True
    )
    
    date = fields.Datetime(
        string='Fecha',
        required=True,
        default=fields.Datetime.now
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='Usuario',
        default=lambda self: self.env.user
    )

