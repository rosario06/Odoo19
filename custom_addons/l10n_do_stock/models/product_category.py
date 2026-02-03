# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductCategory(models.Model):
    _inherit = 'product.category'
    
    l10n_do_dgii_code = fields.Char(
        string='Código DGII',
        help="Código de categoría según clasificación DGII"
    )
    
    l10n_do_default_tax_classification = fields.Selection([
        ('gravado', 'Gravado'),
        ('exento', 'Exento'),
        ('excluido', 'Excluido')
    ], string='Clasificación Fiscal por Defecto',
        help="Clasificación fiscal que se aplicará por defecto a productos de esta categoría")

