# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'
    
    l10n_do_tax_classification = fields.Selection(
        related='product_id.l10n_do_tax_classification',
        string='Clasificación Fiscal',
        store=True,
        readonly=True
    )
    
    l10n_do_itbis_amount = fields.Monetary(
        string='Monto ITBIS',
        compute='_compute_itbis_amount',
        store=True,
        currency_field='company_currency_id'
    )
    
    company_currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        readonly=True
    )
    
    @api.depends('product_id.l10n_do_itbis_percentage', 'product_uom_qty', 'price_unit')
    def _compute_itbis_amount(self):
        for move in self:
            if move.product_id.l10n_do_tax_classification == 'gravado':
                base_amount = move.product_uom_qty * move.price_unit
                itbis_percentage = move.product_id.l10n_do_itbis_percentage or 0.0
                move.l10n_do_itbis_amount = base_amount * (itbis_percentage / 100.0)
            else:
                move.l10n_do_itbis_amount = 0.0

