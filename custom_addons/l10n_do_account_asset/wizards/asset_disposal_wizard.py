# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AssetDisposalWizard(models.TransientModel):
    _name = 'asset.disposal.wizard'
    _description = 'Asistente de Baja de Activo'

    asset_id = fields.Many2one(
        'account.asset',
        string='Activo',
        required=True
    )
    disposal_date = fields.Date(
        string='Fecha de Baja',
        required=True,
        default=fields.Date.context_today
    )
    disposal_type = fields.Selection(
        [
            ('sale', 'Venta'),
            ('scrap', 'Desecho'),
            ('donation', 'Donación'),
            ('loss', 'Pérdida'),
            ('theft', 'Robo'),
        ],
        string='Tipo de Baja',
        required=True,
        default='scrap'
    )
    sale_value = fields.Monetary(
        string='Valor de Venta',
        currency_field='currency_id'
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente'
    )
    notes = fields.Text(
        string='Notas'
    )
    company_id = fields.Many2one(
        'res.company',
        related='asset_id.company_id'
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id'
    )

    def action_dispose_asset(self):
        """Crea la baja del activo"""
        self.ensure_one()
        
        disposal_vals = {
            'asset_id': self.asset_id.id,
            'disposal_date': self.disposal_date,
            'disposal_type': self.disposal_type,
            'sale_value': self.sale_value,
            'partner_id': self.partner_id.id if self.partner_id else False,
            'notes': self.notes,
        }
        
        disposal = self.env['account.asset.disposal'].create(disposal_vals)
        disposal.action_confirm()
        disposal.action_done()
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.asset.disposal',
            'res_id': disposal.id,
            'view_mode': 'form',
            'target': 'current',
        }

