# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class L10nDoConduceWizard(models.TransientModel):
    _name = 'l10n.do.conduce.wizard'
    _description = 'Asistente de Generación de Conduce'
    
    picking_ids = fields.Many2many(
        'stock.picking',
        string='Transferencias',
        required=True,
        domain="[('state', '=', 'assigned'), ('picking_type_code', '=', 'outgoing')]"
    )
    
    date = fields.Date(
        string='Fecha del Conduce',
        required=True,
        default=fields.Date.today
    )
    
    driver_name = fields.Char(
        string='Nombre del Chofer',
        required=True
    )
    
    driver_id_number = fields.Char(
        string='Cédula del Chofer'
    )
    
    driver_license = fields.Char(
        string='Licencia de Conducir'
    )
    
    vehicle_plate = fields.Char(
        string='Placa del Vehículo',
        required=True
    )
    
    vehicle_type = fields.Selection([
        ('truck', 'Camión'),
        ('van', 'Camioneta'),
        ('car', 'Automóvil'),
        ('motorcycle', 'Motocicleta'),
        ('other', 'Otro')
    ], string='Tipo de Vehículo', default='truck')
    
    generation_mode = fields.Selection([
        ('individual', 'Un conduce por transferencia'),
        ('consolidated', 'Un conduce consolidado')
    ], string='Modo de Generación', default='individual', required=True)
    
    origin_address = fields.Text(
        string='Dirección de Origen',
        help="Se usará para el conduce consolidado"
    )
    
    destination_address = fields.Text(
        string='Dirección de Destino',
        help="Se usará para el conduce consolidado"
    )
    
    notes = fields.Text(string='Observaciones')
    
    def action_generate_conduce(self):
        """Generar conduce(s) según el modo seleccionado"""
        self.ensure_one()
        
        if not self.picking_ids:
            raise UserError(_('Debe seleccionar al menos una transferencia.'))
        
        # Validar que las transferencias no tengan conduce ya
        pickings_with_conduce = self.picking_ids.filtered(lambda p: p.l10n_do_conduce_id)
        if pickings_with_conduce:
            raise UserError(_(
                'Las siguientes transferencias ya tienen conduce:\n%s'
            ) % '\n'.join(pickings_with_conduce.mapped('name')))
        
        conduces = self.env['l10n.do.conduce']
        
        if self.generation_mode == 'individual':
            # Generar un conduce por cada transferencia
            for picking in self.picking_ids:
                conduce_vals = self._prepare_conduce_vals(picking)
                conduce = self.env['l10n.do.conduce'].create(conduce_vals)
                picking.l10n_do_conduce_id = conduce.id
                conduces |= conduce
        else:
            # Generar un conduce consolidado
            conduce_vals = self._prepare_consolidated_conduce_vals()
            conduce = self.env['l10n.do.conduce'].create(conduce_vals)
            self.picking_ids.write({'l10n_do_conduce_id': conduce.id})
            conduces = conduce
        
        # Mostrar los conduces generados
        if len(conduces) == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Conduce Generado'),
                'res_model': 'l10n.do.conduce',
                'res_id': conduces.id,
                'view_mode': 'form',
                'target': 'current',
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Conduces Generados'),
                'res_model': 'l10n.do.conduce',
                'domain': [('id', 'in', conduces.ids)],
                'view_mode': 'list,form',
                'target': 'current',
            }
    
    def _prepare_conduce_vals(self, picking):
        """Preparar valores para un conduce individual"""
        line_vals = []
        for move in picking.move_ids:
            line_vals.append((0, 0, {
                'product_id': move.product_id.id,
                'description': move.product_id.name,
                'quantity': move.product_uom_qty,
                'uom_id': move.product_uom.id,
                'weight': move.product_id.weight * move.product_uom_qty,
            }))
        
        return {
            'date': self.date,
            'picking_id': picking.id,
            'partner_id': picking.partner_id.id if picking.partner_id else False,
            'origin_address': picking.location_id.complete_name or '',
            'destination_address': picking.location_dest_id.complete_name or (
                picking.partner_id.contact_address if picking.partner_id else ''
            ),
            'driver_name': self.driver_name,
            'driver_id_number': self.driver_id_number,
            'driver_license': self.driver_license,
            'vehicle_plate': self.vehicle_plate,
            'vehicle_type': self.vehicle_type,
            'notes': self.notes,
            'line_ids': line_vals,
        }
    
    def _prepare_consolidated_conduce_vals(self):
        """Preparar valores para un conduce consolidado"""
        line_vals = []
        
        # Agrupar productos de todas las transferencias
        product_dict = {}
        for picking in self.picking_ids:
            for move in picking.move_ids:
                key = (move.product_id.id, move.product_uom.id)
                if key in product_dict:
                    product_dict[key]['quantity'] += move.product_uom_qty
                    product_dict[key]['weight'] += move.product_id.weight * move.product_uom_qty
                else:
                    product_dict[key] = {
                        'product_id': move.product_id.id,
                        'description': move.product_id.name,
                        'quantity': move.product_uom_qty,
                        'uom_id': move.product_uom.id,
                        'weight': move.product_id.weight * move.product_uom_qty,
                    }
        
        for product_data in product_dict.values():
            line_vals.append((0, 0, product_data))
        
        # Usar el primer picking como referencia
        first_picking = self.picking_ids[0]
        
        return {
            'date': self.date,
            'partner_id': first_picking.partner_id.id if first_picking.partner_id else False,
            'origin_address': self.origin_address or first_picking.location_id.complete_name or '',
            'destination_address': self.destination_address or (
                first_picking.partner_id.contact_address if first_picking.partner_id else ''
            ),
            'driver_name': self.driver_name,
            'driver_id_number': self.driver_id_number,
            'driver_license': self.driver_license,
            'vehicle_plate': self.vehicle_plate,
            'vehicle_type': self.vehicle_type,
            'notes': self.notes or f"Conduce consolidado para transferencias: {', '.join(self.picking_ids.mapped('name'))}",
            'line_ids': line_vals,
        }

