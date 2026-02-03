# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    # Campos Fiscales RD
    l10n_do_tax_classification = fields.Selection([
        ('gravado', 'Gravado'),
        ('exento', 'Exento'),
        ('excluido', 'Excluido')
    ], string='Clasificación Fiscal', default='gravado',
        help="Clasificación fiscal del producto según DGII RD")
    
    l10n_do_tariff_code = fields.Char(
        string='Código Arancelario',
        help="Código arancelario para aduanas (6-8 dígitos)"
    )
    
    l10n_do_product_type = fields.Selection([
        ('finished', 'Producto Terminado'),
        ('raw_material', 'Materia Prima'),
        ('consumable', 'Consumible'),
        ('service', 'Servicio'),
        ('asset', 'Activo Fijo')
    ], string='Tipo de Producto RD',
        help="Clasificación del producto para reportes DGII")
    
    l10n_do_itbis_percentage = fields.Float(
        string='% ITBIS',
        digits=(5, 2),
        help="Porcentaje de ITBIS aplicable (típicamente 18%)"
    )
    
    l10n_do_requires_serial = fields.Boolean(
        string='Requiere Número de Serie',
        help="Marcar si el producto requiere número de serie para trazabilidad DGII"
    )
    
    l10n_do_controlled_product = fields.Boolean(
        string='Producto Controlado',
        help="Producto sujeto a control especial por DGII u otras autoridades"
    )
    
    l10n_do_notes = fields.Text(
        string='Notas Fiscales RD'
    )
    
    @api.onchange('l10n_do_tax_classification')
    def _onchange_tax_classification(self):
        """Actualizar ITBIS según clasificación"""
        if self.l10n_do_tax_classification == 'gravado':
            self.l10n_do_itbis_percentage = 18.0
        else:
            self.l10n_do_itbis_percentage = 0.0

