# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    # Campos para Conduce
    l10n_do_conduce_id = fields.Many2one(
        'l10n.do.conduce',
        string='Conduce',
        readonly=True,
        copy=False,
        help="Documento de transporte asociado"
    )
    
    l10n_do_driver_name = fields.Char(
        string='Chofer',
        help="Nombre del chofer que realiza el transporte"
    )
    
    l10n_do_driver_id = fields.Char(
        string='Cédula Chofer',
        help="Cédula de identidad del chofer"
    )
    
    l10n_do_vehicle_plate = fields.Char(
        string='Placa Vehículo',
        help="Placa del vehículo de transporte"
    )
    
    l10n_do_requires_conduce = fields.Boolean(
        string='Requiere Conduce',
        compute='_compute_requires_conduce',
        store=True,
        help="Indica si esta transferencia requiere un conduce"
    )
    
    # Relación con NCF
    l10n_do_ncf_id = fields.Many2one(
        'account.move',
        string='NCF Relacionado',
        help="Comprobante Fiscal relacionado con esta transferencia"
    )
    
    @api.depends('picking_type_code', 'partner_id')
    def _compute_requires_conduce(self):
        """Determinar si la transferencia requiere conduce"""
        for picking in self:
            # Requiere conduce si es una salida (outgoing) y tiene cliente
            picking.l10n_do_requires_conduce = (
                picking.picking_type_code == 'outgoing' and
                picking.partner_id and
                picking.partner_id.id != picking.company_id.partner_id.id
            )
    
    def action_generate_conduce(self):
        """Generar un conduce para esta transferencia"""
        self.ensure_one()
        
        if self.l10n_do_conduce_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Conduce',
                'res_model': 'l10n.do.conduce',
                'res_id': self.l10n_do_conduce_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
        
        # Crear nuevo conduce
        conduce = self.env['l10n.do.conduce'].create_from_picking(self)
        self.l10n_do_conduce_id = conduce.id
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Conduce Generado',
            'res_model': 'l10n.do.conduce',
            'res_id': conduce.id,
            'view_mode': 'form',
            'target': 'current',
        }

