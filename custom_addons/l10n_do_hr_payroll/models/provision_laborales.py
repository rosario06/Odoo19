# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta


class ProvisionLaborales(models.Model):
    _name = 'provision.laborales'
    _description = 'Provisión de Prestaciones Laborales'
    _order = 'date desc, id desc'
    
    name = fields.Char(
        string='Referencia',
        required=True,
        readonly=True,
        default='New'
    )
    
    employee_id = fields.Many2one(
        'hr.employee',
        string='Empleado',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    
    contract_id = fields.Many2one(
        'hr.contract',
        string='Contrato',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    
    date = fields.Date(
        string='Fecha',
        required=True,
        default=fields.Date.today,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Fecha del aprovisionamiento"
    )
    
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('posted', 'Contabilizado'),
        ('cancelled', 'Cancelado')
    ], string='Estado', default='draft', readonly=True)
    
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        default=lambda self: self.env.company,
        required=True
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        related='company_id.currency_id',
        readonly=True
    )
    
    # Datos del cálculo
    wage = fields.Float(
        string='Salario Base',
        digits=(16, 2),
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Salario mensual del empleado"
    )
    
    months_worked = fields.Float(
        string='Meses Trabajados',
        digits=(16, 2),
        compute='_compute_months_worked',
        store=True,
        help="Meses trabajados desde la fecha de inicio del contrato"
    )
    
    # Cesantía
    cesantia_rate = fields.Float(
        string='Tasa Cesantía (%)',
        digits=(5, 2),
        default=8.33,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Porcentaje mensual para cesantía (aprox 1 mes por año)"
    )
    
    cesantia_amount = fields.Float(
        string='Cesantía',
        digits=(16, 2),
        compute='_compute_provision_amounts',
        store=True,
        help="Monto de cesantía del período"
    )
    
    cesantia_accumulated = fields.Float(
        string='Cesantía Acumulada',
        digits=(16, 2),
        help="Cesantía acumulada histórica"
    )
    
    # Preaviso
    preaviso_rate = fields.Float(
        string='Tasa Preaviso (%)',
        digits=(5, 2),
        default=8.33,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Porcentaje mensual para preaviso (aprox 1 mes por año)"
    )
    
    preaviso_amount = fields.Float(
        string='Preaviso',
        digits=(16, 2),
        compute='_compute_provision_amounts',
        store=True,
        help="Monto de preaviso del período"
    )
    
    preaviso_accumulated = fields.Float(
        string='Preaviso Acumulado',
        digits=(16, 2),
        help="Preaviso acumulado histórico"
    )
    
    # Vacaciones
    vacation_days = fields.Integer(
        string='Días de Vacaciones',
        default=14,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Días de vacaciones por año"
    )
    
    vacaciones_amount = fields.Float(
        string='Vacaciones',
        digits=(16, 2),
        compute='_compute_provision_amounts',
        store=True,
        help="Monto de vacaciones del período"
    )
    
    vacaciones_accumulated = fields.Float(
        string='Vacaciones Acumuladas',
        digits=(16, 2),
        help="Vacaciones acumuladas históricas"
    )
    
    # Salario de Navidad
    salario_navidad_rate = fields.Float(
        string='Tasa Salario Navidad (%)',
        digits=(5, 2),
        default=8.33,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Porcentaje mensual para salario de navidad (aprox 1 mes por año)"
    )
    
    salario_navidad_amount = fields.Float(
        string='Salario Navidad',
        digits=(16, 2),
        compute='_compute_provision_amounts',
        store=True,
        help="Monto de salario de navidad del período"
    )
    
    salario_navidad_accumulated = fields.Float(
        string='Salario Navidad Acumulado',
        digits=(16, 2),
        help="Salario de navidad acumulado histórico"
    )
    
    # Total
    total_provision = fields.Float(
        string='Total Provisión',
        digits=(16, 2),
        compute='_compute_total_provision',
        store=True,
        help="Total de aprovisionamiento del período"
    )
    
    # Contabilidad
    move_id = fields.Many2one(
        'account.move',
        string='Asiento Contable',
        readonly=True
    )
    
    notes = fields.Text(
        string='Notas'
    )
    
    @api.depends('contract_id', 'contract_id.date_start', 'date')
    def _compute_months_worked(self):
        """Calcula los meses trabajados desde el inicio del contrato"""
        for record in self:
            if record.contract_id and record.contract_id.date_start and record.date:
                delta = relativedelta(record.date, record.contract_id.date_start)
                record.months_worked = delta.years * 12 + delta.months + delta.days / 30.0
            else:
                record.months_worked = 0.0
    
    @api.depends('wage', 'cesantia_rate', 'preaviso_rate', 'vacation_days', 'salario_navidad_rate')
    def _compute_provision_amounts(self):
        """Calcula los montos de provisión del período"""
        for record in self:
            # Cesantía: salario * tasa_mensual
            record.cesantia_amount = record.wage * (record.cesantia_rate / 100)
            
            # Preaviso: salario * tasa_mensual
            record.preaviso_amount = record.wage * (record.preaviso_rate / 100)
            
            # Vacaciones: (salario / 30) * (días_vacaciones / 12)
            if record.vacation_days > 0:
                daily_wage = record.wage / 30
                record.vacaciones_amount = daily_wage * (record.vacation_days / 12)
            else:
                record.vacaciones_amount = 0.0
            
            # Salario de Navidad: salario * tasa_mensual
            record.salario_navidad_amount = record.wage * (record.salario_navidad_rate / 100)
    
    @api.depends('cesantia_amount', 'preaviso_amount', 'vacaciones_amount', 'salario_navidad_amount')
    def _compute_total_provision(self):
        """Calcula el total de aprovisionamiento"""
        for record in self:
            record.total_provision = (
                record.cesantia_amount +
                record.preaviso_amount +
                record.vacaciones_amount +
                record.salario_navidad_amount
            )
    
    @api.model_create_multi
    def create(self, vals_list):
        """Asigna secuencia al crear"""
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('provision.laborales') or 'New'
        return super().create(vals_list)
    
    def action_confirm(self):
        """Confirma la provisión"""
        self.write({'state': 'confirmed'})
    
    def action_post(self):
        """Genera el asiento contable y marca como contabilizado"""
        for record in self:
            if record.state != 'confirmed':
                continue
            
            # TODO: Crear asiento contable
            # move = record._create_accounting_move()
            # record.write({'move_id': move.id, 'state': 'posted'})
            
            # Por ahora solo cambiamos el estado
            record.write({'state': 'posted'})
    
    def action_cancel(self):
        """Cancela la provisión"""
        self.write({'state': 'cancelled'})
    
    def action_draft(self):
        """Vuelve a borrador"""
        self.write({'state': 'draft'})

