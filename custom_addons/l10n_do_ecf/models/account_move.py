# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    # e-CF
    ecf_document_id = fields.Many2one(
        'ecf.document',
        string='Documento e-CF',
        readonly=True,
        copy=False
    )
    
    ecf_state = fields.Selection(
        related='ecf_document_id.state',
        string='Estado e-CF',
        store=True
    )
    
    ecf_number = fields.Char(
        related='ecf_document_id.ecf_number',
        string='e-NCF',
        store=True
    )
    
    has_ecf = fields.Boolean(
        string='Tiene e-CF',
        compute='_compute_has_ecf',
        store=True
    )
    
    can_send_ecf = fields.Boolean(
        string='Puede Enviar e-CF',
        compute='_compute_can_send_ecf'
    )

    @api.depends('ecf_document_id')
    def _compute_has_ecf(self):
        for record in self:
            record.has_ecf = bool(record.ecf_document_id)

    @api.depends('state', 'move_type', 'company_id.l10n_do_ecf_enabled', 'country_code')
    def _compute_can_send_ecf(self):
        for record in self:
            record.can_send_ecf = (
                record.state == 'posted' and
                record.move_type in ['out_invoice', 'out_refund'] and
                record.company_id.l10n_do_ecf_enabled and
                record.country_code == 'DO' and
                not record.has_ecf
            )

    def action_create_ecf_document(self):
        """Crea el documento e-CF asociado a esta factura"""
        self.ensure_one()
        
        if not self.can_send_ecf:
            raise UserError(_('Esta factura no cumple los requisitos para generar e-CF.'))
        
        if self.ecf_document_id:
            raise UserError(_('Esta factura ya tiene un documento e-CF asociado.'))
        
        # Determinar tipo de e-CF según tipo de documento
        document_type_map = {
            ('01', 'out_invoice'): '31',  # e-Factura de Crédito Fiscal
            ('02', 'out_invoice'): '32',  # e-Factura de Consumo
            ('03', 'out_invoice'): '33',  # e-Nota de Débito
            ('04', 'out_refund'): '34',   # e-Nota de Crédito
            ('14', 'out_invoice'): '44',  # e-Régimen Especial
            ('15', 'out_invoice'): '45',  # e-Gubernamental
        }
        
        # Obtener tipo de NCF actual
        ncf_type = self.l10n_latam_document_type_id.code if self.l10n_latam_document_type_id else '01'
        ecf_type = document_type_map.get((ncf_type, self.move_type), '31')
        
        # Crear documento e-CF
        ecf_document = self.env['ecf.document'].create({
            'name': self.name,
            'invoice_id': self.id,
            'company_id': self.company_id.id,
            'document_type': ecf_type,
            'date': self.invoice_date or fields.Date.today(),
        })
        
        self.ecf_document_id = ecf_document.id
        
        return {
            'name': _('Documento e-CF'),
            'type': 'ir.actions.act_window',
            'res_model': 'ecf.document',
            'res_id': ecf_document.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_ecf_document(self):
        """Abre el documento e-CF asociado"""
        self.ensure_one()
        
        if not self.ecf_document_id:
            raise UserError(_('Esta factura no tiene un documento e-CF asociado.'))
        
        return {
            'name': _('Documento e-CF'),
            'type': 'ir.actions.act_window',
            'res_model': 'ecf.document',
            'res_id': self.ecf_document_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_send_ecf_wizard(self):
        """Abre el wizard de envío de e-CF"""
        self.ensure_one()
        
        if not self.ecf_document_id:
            # Crear documento si no existe
            self.action_create_ecf_document()
        
        return {
            'name': _('Enviar e-CF a DGII'),
            'type': 'ir.actions.act_window',
            'res_model': 'ecf.send.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_invoice_ids': [(6, 0, [self.id])],
            }
        }

