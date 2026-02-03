# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountAssetCategory(models.Model):
    _name = 'account.asset.category'
    _description = 'Categoría de Activos Fijos'
    _order = 'name'

    name = fields.Char(
        string='Nombre',
        required=True,
        translate=True
    )
    code = fields.Char(
        string='Código',
        required=True,
        size=10
    )
    depreciation_rate = fields.Float(
        string='Tasa de Depreciación (%)',
        required=True,
        help='Tasa anual de depreciación según DGII'
    )
    depreciation_method = fields.Selection(
        [
            ('linear', 'Lineal'),
            ('degressive', 'Decreciente/Acelerado'),
        ],
        string='Método de Depreciación',
        required=True,
        default='linear',
        help='Método de cálculo de depreciación'
    )
    useful_life_years = fields.Integer(
        string='Vida Útil (Años)',
        compute='_compute_useful_life_years',
        store=True,
        help='Vida útil calculada automáticamente según tasa'
    )
    
    # Cuentas contables
    account_asset_id = fields.Many2one(
        'account.account',
        string='Cuenta de Activo',
        domain="[('account_type', '=', 'asset_fixed')]",
        help='Cuenta donde se registra el activo'
    )
    account_depreciation_id = fields.Many2one(
        'account.account',
        string='Cuenta de Depreciación Acumulada',
        domain="[('account_type', '=', 'asset_fixed')]",
        help='Cuenta de depreciación acumulada'
    )
    account_depreciation_expense_id = fields.Many2one(
        'account.account',
        string='Cuenta de Gasto por Depreciación',
        domain="[('account_type', 'in', ['expense', 'expense_direct_cost'])]",
        help='Cuenta de gasto por depreciación'
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Diario',
        domain="[('type', '=', 'general')]",
        help='Diario para asientos de depreciación'
    )
    
    # Configuración adicional
    active = fields.Boolean(
        default=True
    )
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        default=lambda self: self.env.company,
        required=True
    )
    
    # Estadísticas
    asset_count = fields.Integer(
        string='Número de Activos',
        compute='_compute_asset_count'
    )
    
    note = fields.Text(
        string='Notas',
        help='Información adicional sobre la categoría'
    )

    _sql_constraints = [
        ('code_unique', 'unique(code, company_id)', 'El código de categoría debe ser único por compañía!'),
    ]

    @api.depends('depreciation_rate')
    def _compute_useful_life_years(self):
        """Calcula la vida útil en años según la tasa de depreciación"""
        for record in self:
            if record.depreciation_rate > 0:
                record.useful_life_years = int(100 / record.depreciation_rate)
            else:
                record.useful_life_years = 0

    def _compute_asset_count(self):
        """Cuenta los activos de cada categoría"""
        for record in self:
            record.asset_count = self.env['account.asset'].search_count([
                ('category_id', '=', record.id)
            ])

    @api.constrains('depreciation_rate')
    def _check_depreciation_rate(self):
        """Valida que la tasa de depreciación esté en rango válido"""
        for record in self:
            if not (0 < record.depreciation_rate <= 100):
                raise ValidationError(_('La tasa de depreciación debe estar entre 0 y 100%.'))

    def action_view_assets(self):
        """Acción para ver los activos de esta categoría"""
        self.ensure_one()
        return {
            'name': _('Activos'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.asset',
            'view_mode': 'list,form',
            'domain': [('category_id', '=', self.id)],
            'context': {'default_category_id': self.id},
        }

