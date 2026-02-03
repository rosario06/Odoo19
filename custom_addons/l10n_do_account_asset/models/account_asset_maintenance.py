# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountAssetMaintenance(models.Model):
    _name = 'account.asset.maintenance'
    _description = 'Mantenimiento de Activo'
    _order = 'maintenance_date desc'

    name = fields.Char(
        string='Descripción',
        required=True
    )
    asset_id = fields.Many2one(
        'account.asset',
        string='Activo',
        required=True,
        ondelete='cascade'
    )
    maintenance_type = fields.Selection(
        [
            ('preventive', 'Preventivo'),
            ('corrective', 'Correctivo'),
            ('predictive', 'Predictivo'),
        ],
        string='Tipo',
        required=True,
        default='preventive'
    )
    maintenance_date = fields.Date(
        string='Fecha',
        required=True,
        default=fields.Date.context_today
    )
    next_maintenance_date = fields.Date(
        string='Próximo Mantenimiento'
    )
    cost = fields.Monetary(
        string='Costo',
        currency_field='currency_id'
    )
    provider_id = fields.Many2one(
        'res.partner',
        string='Proveedor'
    )
    invoice_id = fields.Many2one(
        'account.move',
        string='Factura',
        domain="[('move_type', '=', 'in_invoice')]"
    )
    responsible_id = fields.Many2one(
        'res.users',
        string='Responsable',
        default=lambda self: self.env.user
    )
    state = fields.Selection(
        [
            ('scheduled', 'Programado'),
            ('in_progress', 'En Progreso'),
            ('done', 'Completado'),
            ('cancelled', 'Cancelado'),
        ],
        string='Estado',
        default='scheduled',
        required=True
    )
    notes = fields.Text(
        string='Notas'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        related='asset_id.company_id',
        store=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        related='company_id.currency_id'
    )

    def action_start(self):
        """Inicia el mantenimiento"""
        self.write({'state': 'in_progress'})

    def action_done(self):
        """Completa el mantenimiento"""
        for maintenance in self:
            maintenance.write({'state': 'done'})
            if maintenance.next_maintenance_date:
                maintenance.asset_id.write({'next_maintenance_date': maintenance.next_maintenance_date})

    def action_cancel(self):
        """Cancela el mantenimiento"""
        self.write({'state': 'cancelled'})

    def action_reschedule(self):
        """Reprograma el mantenimiento"""
        self.write({'state': 'scheduled'})

