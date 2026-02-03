# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountAssetDisposal(models.Model):
    _name = 'account.asset.disposal'
    _description = 'Baja de Activo Fijo'
    _order = 'disposal_date desc'

    name = fields.Char(
        string='Referencia',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Nuevo')
    )
    asset_id = fields.Many2one(
        'account.asset',
        string='Activo',
        required=True,
        ondelete='restrict'
    )
    disposal_date = fields.Date(
        string='Fecha de Baja',
        required=True,
        default=fields.Date.context_today
    )
    disposal_type = fields.Selection(
        [
            ('sale', 'Venta'),
            ('scrap', 'Desecho'),
            ('donation', 'Donación'),
            ('loss', 'Pérdida'),
            ('theft', 'Robo'),
        ],
        string='Tipo de Baja',
        required=True,
        default='scrap'
    )
    
    # Valores
    book_value = fields.Monetary(
        string='Valor en Libros',
        currency_field='currency_id',
        readonly=True
    )
    sale_value = fields.Monetary(
        string='Valor de Venta',
        currency_field='currency_id'
    )
    gain_loss = fields.Monetary(
        string='Ganancia/Pérdida',
        compute='_compute_gain_loss',
        currency_field='currency_id',
        store=True
    )
    
    # Venta
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente'
    )
    invoice_id = fields.Many2one(
        'account.move',
        string='Factura de Venta',
        domain="[('move_type', '=', 'out_invoice')]"
    )
    
    # Contabilidad
    move_id = fields.Many2one(
        'account.move',
        string='Asiento Contable',
        readonly=True
    )
    state = fields.Selection(
        [
            ('draft', 'Borrador'),
            ('confirmed', 'Confirmado'),
            ('done', 'Finalizado'),
            ('cancelled', 'Cancelado'),
        ],
        string='Estado',
        default='draft',
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

    @api.model_create_multi
    def create(self, vals_list):
        """Asigna secuencia"""
        for vals in vals_list:
            if vals.get('name', _('Nuevo')) == _('Nuevo'):
                vals['name'] = self.env['ir.sequence'].next_by_code('account.asset.disposal') or _('Nuevo')
        return super().create(vals_list)

    @api.depends('book_value', 'sale_value')
    def _compute_gain_loss(self):
        """Calcula ganancia o pérdida"""
        for disposal in self:
            disposal.gain_loss = disposal.sale_value - disposal.book_value

    def action_confirm(self):
        """Confirma la baja"""
        for disposal in self:
            if disposal.asset_id.state != 'running':
                raise UserError(_('Solo puede dar de baja activos en uso.'))
            
            disposal.book_value = disposal.asset_id.book_value
            disposal.write({'state': 'confirmed'})

    def action_done(self):
        """Finaliza la baja y genera asientos"""
        for disposal in self:
            # Crea asiento contable de baja
            disposal._create_disposal_move()
            
            # Actualiza estado del activo
            disposal.asset_id.write({'state': 'disposed'})
            
            disposal.write({'state': 'done'})

    def _create_disposal_move(self):
        """Crea asiento contable de baja de activo"""
        self.ensure_one()
        
        # TO-DO: Implementar creación de asiento contable
        # Este es un método complejo que requiere configuración de cuentas
        pass

    def action_cancel(self):
        """Cancela la baja"""
        for disposal in self:
            if disposal.move_id:
                disposal.move_id.button_cancel()
                disposal.move_id.unlink()
            disposal.write({'state': 'cancelled'})

    def action_draft(self):
        """Vuelve a borrador"""
        self.write({'state': 'draft'})

