# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class L10nDoConduce(models.Model):
    _name = 'l10n.do.conduce'
    _description = 'Conduce (Documento de Transporte RD)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, name desc'
    
    name = fields.Char(
        string='Número de Conduce',
        required=True,
        readonly=True,
        copy=False,
        default='New',
        tracking=True
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env.company
    )
    
    date = fields.Date(
        string='Fecha',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=fields.Date.today,
        tracking=True
    )
    
    # Información del Transporte
    origin_address = fields.Text(
        string='Dirección de Origen',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    
    destination_address = fields.Text(
        string='Dirección de Destino',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    
    driver_name = fields.Char(
        string='Nombre del Chofer',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        tracking=True
    )
    
    driver_id_number = fields.Char(
        string='Cédula del Chofer',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Cédula de identidad del chofer"
    )
    
    driver_license = fields.Char(
        string='Licencia de Conducir',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    
    vehicle_plate = fields.Char(
        string='Placa del Vehículo',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        tracking=True
    )
    
    vehicle_type = fields.Selection([
        ('truck', 'Camión'),
        ('van', 'Camioneta'),
        ('car', 'Automóvil'),
        ('motorcycle', 'Motocicleta'),
        ('other', 'Otro')
    ], string='Tipo de Vehículo',
        readonly=True,
        states={'draft': [('readonly', False)]})
    
    # Relaciones
    picking_id = fields.Many2one(
        'stock.picking',
        string='Transferencia de Inventario',
        readonly=True,
        states={'draft': [('readonly', False)]},
        ondelete='restrict',
        help="Transferencia de inventario asociada"
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente/Proveedor',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    
    ncf_id = fields.Many2one(
        'account.move',
        string='NCF Relacionado',
        readonly=True,
        help="Comprobante Fiscal (NCF) relacionado"
    )
    
    # Líneas de productos
    line_ids = fields.One2many(
        'l10n.do.conduce.line',
        'conduce_id',
        string='Líneas de Productos',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    
    # Información adicional
    notes = fields.Text(
        string='Observaciones',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('done', 'Entregado'),
        ('cancelled', 'Cancelado')
    ], string='Estado', default='draft', readonly=True, tracking=True)
    
    # Campos computados
    total_qty = fields.Float(
        string='Cantidad Total',
        compute='_compute_totals',
        store=True
    )
    
    total_weight = fields.Float(
        string='Peso Total (kg)',
        compute='_compute_totals',
        store=True
    )
    
    @api.depends('line_ids.quantity', 'line_ids.weight')
    def _compute_totals(self):
        for record in self:
            record.total_qty = sum(line.quantity for line in record.line_ids)
            record.total_weight = sum(line.weight for line in record.line_ids)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('l10n.do.conduce') or 'New'
        return super().create(vals_list)
    
    def action_confirm(self):
        """Confirmar el conduce"""
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_('Debe agregar al menos una línea de producto.'))
        self.write({'state': 'confirmed'})
    
    def action_done(self):
        """Marcar como entregado"""
        self.ensure_one()
        if self.state != 'confirmed':
            raise UserError(_('Solo se pueden entregar conduces confirmados.'))
        self.write({'state': 'done'})
    
    def action_cancel(self):
        """Cancelar el conduce"""
        self.ensure_one()
        if self.state == 'done':
            raise UserError(_('No se puede cancelar un conduce ya entregado.'))
        self.write({'state': 'cancelled'})
    
    def action_draft(self):
        """Volver a borrador"""
        self.ensure_one()
        self.write({'state': 'draft'})
    
    @api.model
    def create_from_picking(self, picking):
        """
        Crear un conduce desde una transferencia de inventario
        
        :param picking: Recordset de stock.picking
        :return: Recordset de l10n.do.conduce creado
        """
        if not picking:
            return self.env['l10n.do.conduce']
        
        vals = {
            'picking_id': picking.id,
            'partner_id': picking.partner_id.id if picking.partner_id else False,
            'origin_address': picking.location_id.name,
            'destination_address': picking.location_dest_id.name,
            'driver_name': picking.l10n_do_driver_name if hasattr(picking, 'l10n_do_driver_name') else '',
            'vehicle_plate': picking.l10n_do_vehicle_plate if hasattr(picking, 'l10n_do_vehicle_plate') else '',
            'date': picking.scheduled_date or fields.Date.today(),
            'line_ids': [(0, 0, {
                'product_id': move.product_id.id,
                'quantity': move.product_uom_qty,
                'uom_id': move.product_uom.id,
                'description': move.product_id.name,
            }) for move in picking.move_ids]
        }
        
        return self.create(vals)


class L10nDoConduceLine(models.Model):
    _name = 'l10n.do.conduce.line'
    _description = 'Línea de Conduce'
    _order = 'sequence, id'
    
    sequence = fields.Integer(string='Secuencia', default=10)
    
    conduce_id = fields.Many2one(
        'l10n.do.conduce',
        string='Conduce',
        required=True,
        ondelete='cascade'
    )
    
    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        required=True
    )
    
    description = fields.Text(
        string='Descripción',
        required=True
    )
    
    quantity = fields.Float(
        string='Cantidad',
        required=True,
        default=1.0,
        digits='Product Unit of Measure'
    )
    
    uom_id = fields.Many2one(
        'uom.uom',
        string='Unidad de Medida',
        required=True
    )
    
    weight = fields.Float(
        string='Peso (kg)',
        digits=(16, 2)
    )
    
    lot_id = fields.Many2one(
        'stock.lot',
        string='Lote/Serie',
        help="Número de lote o serie del producto"
    )
    
    notes = fields.Char(string='Notas')
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.description = self.product_id.name
            self.uom_id = self.product_id.uom_id.id
            self.weight = self.product_id.weight

