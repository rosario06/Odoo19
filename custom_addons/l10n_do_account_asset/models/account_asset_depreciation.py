# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountAssetDepreciation(models.Model):
    _name = 'account.asset.depreciation'
    _description = 'Línea de Depreciación de Activo'
    _order = 'depreciation_date desc'

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
    depreciation_date = fields.Date(
        string='Fecha de Depreciación',
        required=True
    )
    amount = fields.Monetary(
        string='Monto',
        required=True,
        currency_field='currency_id'
    )
    state = fields.Selection(
        [
            ('draft', 'Borrador'),
            ('posted', 'Contabilizado'),
            ('cancelled', 'Cancelado'),
        ],
        string='Estado',
        default='draft',
        required=True
    )
    move_id = fields.Many2one(
        'account.move',
        string='Asiento Contable',
        readonly=True
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

    def action_post(self):
        """Contabiliza la depreciación"""
        for line in self:
            if line.state != 'draft':
                raise UserError(_('Solo se pueden contabilizar líneas en borrador.'))
            
            if not line.asset_id.account_depreciation_id:
                raise UserError(_('Configure la cuenta de depreciación en la categoría del activo.'))
            
            if not line.asset_id.category_id.account_depreciation_expense_id:
                raise UserError(_('Configure la cuenta de gasto por depreciación en la categoría del activo.'))
            
            # Crea asiento contable
            move_vals = {
                'date': line.depreciation_date,
                'journal_id': line.asset_id.journal_id.id,
                'ref': line.name,
                'asset_id': line.asset_id.id,
                'line_ids': [
                    (0, 0, {
                        'name': f'{line.name} - Gasto',
                        'account_id': line.asset_id.category_id.account_depreciation_expense_id.id,
                        'debit': line.amount,
                        'credit': 0.0,
                    }),
                    (0, 0, {
                        'name': f'{line.name} - Depreciación Acumulada',
                        'account_id': line.asset_id.account_depreciation_id.id,
                        'debit': 0.0,
                        'credit': line.amount,
                    }),
                ],
            }
            
            move = self.env['account.move'].create(move_vals)
            move.action_post()
            
            line.write({
                'state': 'posted',
                'move_id': move.id,
            })

    def action_cancel(self):
        """Cancela la depreciación"""
        for line in self:
            if line.move_id and line.move_id.state == 'posted':
                line.move_id.button_cancel()
                line.move_id.unlink()
            
            line.write({
                'state': 'cancelled',
                'move_id': False,
            })

    def action_draft(self):
        """Vuelve a borrador"""
        for line in self:
            if line.move_id:
                raise UserError(_('No puede volver a borrador una línea con asiento contable. Cancele primero.'))
            line.write({'state': 'draft'})

    def unlink(self):
        """Previene eliminación de líneas contabilizadas"""
        for line in self:
            if line.state == 'posted':
                raise UserError(_('No puede eliminar líneas de depreciación contabilizadas. Cancele primero.'))
        return super().unlink()

