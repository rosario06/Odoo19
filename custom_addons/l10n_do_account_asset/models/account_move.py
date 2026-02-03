# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    asset_id = fields.Many2one(
        'account.asset',
        string='Activo Relacionado',
        help='Activo fijo relacionado con este asiento'
    )
    can_create_asset = fields.Boolean(
        string='Puede Crear Activo',
        compute='_compute_can_create_asset'
    )

    @api.depends('move_type', 'state', 'line_ids')
    def _compute_can_create_asset(self):
        """Determina si se puede crear un activo desde esta factura"""
        for move in self:
            move.can_create_asset = (
                move.move_type == 'in_invoice' and
                move.state == 'posted' and
                not move.asset_id and
                any(line.product_id.can_be_asset for line in move.line_ids if line.product_id)
            )

    def action_create_asset(self):
        """Crea un activo fijo desde una factura de compra"""
        self.ensure_one()
        
        if not self.can_create_asset:
            return
        
        # Busca la línea principal (mayor monto)
        asset_line = max(
            self.invoice_line_ids.filtered(lambda l: l.product_id and l.product_id.can_be_asset),
            key=lambda l: l.price_subtotal,
            default=None
        )
        
        if not asset_line:
            return
        
        # Valores del activo
        asset_vals = {
            'name': asset_line.name or asset_line.product_id.name,
            'category_id': asset_line.product_id.asset_category_id.id if asset_line.product_id.asset_category_id else False,
            'acquisition_date': self.invoice_date or fields.Date.context_today(self),
            'first_depreciation_date': self.invoice_date or fields.Date.context_today(self),
            'purchase_value': asset_line.price_subtotal,
            'invoice_id': self.id,
        }
        
        # Crea el activo
        asset = self.env['account.asset'].create(asset_vals)
        self.asset_id = asset.id
        
        # Abre el activo creado
        return {
            'name': _('Activo Fijo'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.asset',
            'res_id': asset.id,
            'view_mode': 'form',
            'target': 'current',
        }


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # Este campo se puede usar para vincular líneas específicas con activos
    asset_id = fields.Many2one(
        'account.asset',
        string='Activo',
        help='Activo fijo relacionado con esta línea'
    )

