# -*- coding: utf-8 -*-

from odoo import models, fields, api


class L10nDoStockValuation(models.Model):
    _name = 'l10n.do.stock.valuation'
    _description = 'Valorización de Inventario RD'
    _order = 'date desc, product_id'
    
    name = fields.Char(
        string='Referencia',
        required=True,
        readonly=True,
        default='New'
    )
    
    date = fields.Date(
        string='Fecha',
        required=True,
        default=fields.Date.today,
        readonly=True
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        readonly=True,
        default=lambda self: self.env.company
    )
    
    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        required=True,
        readonly=True
    )
    
    location_id = fields.Many2one(
        'stock.location',
        string='Ubicación',
        readonly=True
    )
    
    quantity = fields.Float(
        string='Cantidad',
        digits='Product Unit of Measure',
        readonly=True
    )
    
    unit_cost = fields.Float(
        string='Costo Unitario',
        digits='Product Price',
        readonly=True
    )
    
    total_value = fields.Float(
        string='Valor Total',
        compute='_compute_total_value',
        store=True,
        digits='Product Price'
    )
    
    valuation_method = fields.Selection([
        ('fifo', 'PEPS (Primero en Entrar, Primero en Salir)'),
        ('average', 'Costo Promedio Ponderado'),
        ('standard', 'Costo Estándar')
    ], string='Método de Valorización', readonly=True)
    
    @api.depends('quantity', 'unit_cost')
    def _compute_total_value(self):
        for record in self:
            record.total_value = record.quantity * record.unit_cost
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('l10n.do.stock.valuation') or 'New'
        return super().create(vals_list)

