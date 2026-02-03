# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    # --- Campos para el NCF ---
    # Usamos el campo del módulo latam_base, que es el estándar moderno.
    # Lo renombramos para mayor claridad en la vista.
    ncf = fields.Char(
        string='NCF',
        related='l10n_latam_document_number',
        store=False, # No se almacena, es solo para visualización
        readonly=True,
    )
    
    # Campo computado para saber si la factura es fiscal (usa NCF)
    is_l10n_do_fiscal_invoice = fields.Boolean(
        string='Es Factura Fiscal DO',
        compute='_compute_is_l10n_do_fiscal_invoice',
        store=True,
    )
    
    # Campos para Facturación Electrónica (e-CF)
    l10n_do_ecf_number = fields.Char(
        string='Número e-CF',
        readonly=True,
        copy=False,
        help='Número de e-CF asignado por DGII',
    )
    
    l10n_do_ecf_status = fields.Selection([
        ('pending', 'Pendiente'),
        ('sent', 'Enviado'),
        ('accepted', 'Aceptado por DGII'),
        ('rejected', 'Rechazado por DGII'),
        ('cancelled', 'Anulado'),
    ], string='Estado e-CF', default='pending', readonly=True, copy=False)
    
    l10n_do_ecf_send_date = fields.Datetime(
        string='Fecha de Envío e-CF',
        readonly=True,
        copy=False,
    )
    
    l10n_do_ecf_response_date = fields.Datetime(
        string='Fecha Respuesta DGII',
        readonly=True,
        copy=False,
    )
    
    l10n_do_ecf_trackid = fields.Char(
        string='TrackID DGII',
        readonly=True,
        copy=False,
        help='Identificador de seguimiento asignado por DGII',
    )
    
    l10n_do_ecf_qr_code = fields.Binary(
        string='Código QR',
        readonly=True,
        copy=False,
        help='Código QR para consulta del e-CF',
    )
    
    l10n_do_ecf_xml_file = fields.Binary(
        string='Archivo XML',
        readonly=True,
        copy=False,
    )
    
    l10n_do_ecf_xml_filename = fields.Char(
        string='Nombre Archivo XML',
        readonly=True,
        copy=False,
    )
    
    l10n_do_ncf_sequence_id = fields.Many2one(
        'l10n.do.ncf.sequence',
        string='Secuencia NCF',
        readonly=True,
        copy=False,
    )

    @api.depends('country_code', 'move_type')
    def _compute_is_l10n_do_fiscal_invoice(self):
        """Determina si la factura debe regirse por las reglas del NCF."""
        for move in self:
            # Es una factura fiscal si es de República Dominicana y es una factura de cliente/proveedor
            move.is_l10n_do_fiscal_invoice = move.country_code == 'DO' and move.is_invoice(include_receipts=True)

    @api.model_create_multi
    def create(self, vals_list):
        """Sobreescribimos el create para asignar el tipo de documento LATAM."""
        for vals in vals_list:
            # Si es una factura de cliente y la compañía es Dominicana
            if vals.get('move_type') in ('out_invoice', 'out_refund') and vals.get('company_id'):
                company = self.env['res.company'].browse(vals['company_id'])
                if company.country_id.code == 'DO':
                    # Asignamos el tipo de documento por defecto (Factura de Crédito Fiscal)
                    # Esto se puede hacer más dinámico según el diario
                    journal_id = vals.get('journal_id')
                    if journal_id:
                        journal = self.env['account.journal'].browse(journal_id)
                        if journal.l10n_latam_use_documents:
                            vals['l10n_latam_document_type_id'] = journal.l10n_latam_document_type_id.id
        return super().create(vals_list)

    def action_post(self):
        """Validaciones antes de publicar una factura."""
        for move in self:
            if move.is_l10n_do_fiscal_invoice:
                # 1. Validar que el cliente/proveedor tenga RNC/Cédula
                if not move.partner_id.vat:
                    raise UserError(_("El cliente/proveedor '%s' debe tener un RNC o Cédula para emitir una factura fiscal.") % move.partner_id.name)

                # 2. Validar que se haya asignado un NCF (esto lo gestiona la secuencia)
                if not move.l10n_latam_document_number:
                    raise UserError(_("No se pudo generar un NCF para esta factura. Verifique la configuración del diario y las secuencias."))

                # 3. (Opcional pero recomendado) Validar formato del NCF con una expresión regular
                # Ejemplo para validar B0100000001
                # import re
                # ncf_pattern = re.compile(r'^[A-Z]\d{2}\d{8}$')
                # if not ncf_pattern.match(move.l10n_latam_document_number):
                #     raise ValidationError(_("El formato del NCF %s es inválido.") % move.l10n_latam_document_number)

        result = super().action_post()
        
        # Generar código QR si está habilitado e-CF
        for move in self:
            if move.is_l10n_do_fiscal_invoice and move.company_id.l10n_do_ecf_enabled:
                move._generate_qr_code()
        
        return result

    def _generate_qr_code(self):
        """Genera el código QR para la factura."""
        self.ensure_one()
        if self.l10n_latam_document_number and not self.l10n_do_ecf_qr_code:
            try:
                qr_generator = self.env['l10n.do.qr.generator']
                self.l10n_do_ecf_qr_code = qr_generator.generate_qr_code(self)
            except Exception as e:
                # Log error but don't block posting
                _logger.warning(f"No se pudo generar el código QR para {self.name}: {str(e)}")

    def action_generate_ecf_qr(self):
        """Acción manual para generar código QR."""
        self.ensure_one()
        self._generate_qr_code()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Código QR Generado'),
                'message': _('El código QR se ha generado exitosamente.'),
                'type': 'success',
                'sticky': False,
            }
        }