# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    # Configuración de activos fijos
    asset_journal_id = fields.Many2one(
        'account.journal',
        string='Diario de Activos por Defecto',
        domain="[('type', '=', 'general')]",
        help='Diario usado por defecto para asientos de depreciación'
    )
    asset_account_id = fields.Many2one(
        'account.account',
        string='Cuenta de Activos por Defecto',
        domain="[('account_type', '=', 'asset_fixed')]"
    )
    asset_depreciation_account_id = fields.Many2one(
        'account.account',
        string='Cuenta de Depreciación Acumulada por Defecto',
        domain="[('account_type', '=', 'asset_fixed')]"
    )
    asset_depreciation_expense_account_id = fields.Many2one(
        'account.account',
        string='Cuenta de Gasto por Depreciación por Defecto',
        domain="[('account_type', 'in', ['expense', 'expense_direct_cost'])]"
    )

