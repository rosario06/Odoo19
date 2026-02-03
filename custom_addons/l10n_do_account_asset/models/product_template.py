# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    can_be_asset = fields.Boolean(
        string='Puede ser Activo Fijo',
        help='Permite crear un activo fijo desde una factura de compra de este producto'
    )
    asset_category_id = fields.Many2one(
        'account.asset.category',
        string='Categoría de Activo',
        help='Categoría de activo fijo por defecto para este producto'
    )

