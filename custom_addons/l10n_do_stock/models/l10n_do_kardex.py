# -*- coding: utf-8 -*-

from odoo import models, fields, api


class L10nDoKardex(models.Model):
    _name = 'l10n.do.kardex'
    _description = 'Kardex de Inventario RD'
    _order = 'date desc, product_id'
    _rec_name = 'product_id'
    
    date = fields.Datetime(
        string='Fecha',
        required=True,
        readonly=True,
        index=True
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
        readonly=True,
        index=True
    )
    
    location_id = fields.Many2one(
        'stock.location',
        string='Ubicación',
        required=True,
        readonly=True
    )
    
    move_id = fields.Many2one(
        'stock.move',
        string='Movimiento de Inventario',
        readonly=True,
        ondelete='cascade'
    )
    
    picking_id = fields.Many2one(
        'stock.picking',
        string='Transferencia',
        related='move_id.picking_id',
        store=True,
        readonly=True
    )
    
    reference = fields.Char(
        string='Referencia',
        readonly=True
    )
    
    # Movimiento
    move_type = fields.Selection([
        ('in', 'Entrada'),
        ('out', 'Salida'),
        ('adjustment', 'Ajuste')
    ], string='Tipo de Movimiento', required=True, readonly=True)
    
    # Cantidades
    qty_in = fields.Float(
        string='Cantidad Entrada',
        digits='Product Unit of Measure',
        readonly=True
    )
    
    qty_out = fields.Float(
        string='Cantidad Salida',
        digits='Product Unit of Measure',
        readonly=True
    )
    
    qty_balance = fields.Float(
        string='Saldo Cantidad',
        digits='Product Unit of Measure',
        readonly=True
    )
    
    # Valores
    unit_cost = fields.Float(
        string='Costo Unitario',
        digits='Product Price',
        readonly=True
    )
    
    value_in = fields.Float(
        string='Valor Entrada',
        digits='Product Price',
        readonly=True
    )
    
    value_out = fields.Float(
        string='Valor Salida',
        digits='Product Price',
        readonly=True
    )
    
    value_balance = fields.Float(
        string='Saldo Valor',
        digits='Product Price',
        readonly=True
    )
    
    # Información adicional
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente/Proveedor',
        readonly=True
    )
    
    lot_id = fields.Many2one(
        'stock.lot',
        string='Lote/Serie',
        readonly=True
    )
    
    notes = fields.Text(
        string='Notas',
        readonly=True
    )

