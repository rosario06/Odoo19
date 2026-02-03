# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TSSRateConfig(models.Model):
    _name = 'tss.rate.config'
    _description = 'Configuración de Tasas TSS'
    _order = 'date_from desc, id desc'
    
    name = fields.Char(
        string='Descripción',
        required=True,
        help="Descripción de la configuración (ej: 'Tasas TSS 2025')"
    )
    
    date_from = fields.Date(
        string='Válido Desde',
        required=True,
        default=fields.Date.today,
        help="Fecha desde la cual aplica esta configuración"
    )
    
    date_to = fields.Date(
        string='Válido Hasta',
        help="Fecha hasta la cual aplica esta configuración. Dejar vacío si es indefinido"
    )
    
    active = fields.Boolean(
        string='Activo',
        default=True
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        default=lambda self: self.env.company,
        required=True
    )
    
    # AFP (Administradora de Fondos de Pensiones)
    afp_employee_rate = fields.Float(
        string='AFP Empleado (%)',
        required=True,
        digits=(5, 2),
        default=2.87,
        help="Porcentaje de aporte del empleado a AFP"
    )
    
    afp_employer_rate = fields.Float(
        string='AFP Empleador (%)',
        required=True,
        digits=(5, 2),
        default=7.10,
        help="Porcentaje de aporte del empleador a AFP"
    )
    
    # ARS (Administradora de Riesgos de Salud)
    ars_employee_rate = fields.Float(
        string='ARS Empleado (%)',
        required=True,
        digits=(5, 2),
        default=3.04,
        help="Porcentaje de aporte del empleado a ARS"
    )
    
    ars_employer_rate = fields.Float(
        string='ARS Empleador (%)',
        required=True,
        digits=(5, 2),
        default=7.09,
        help="Porcentaje de aporte del empleador a ARS"
    )
    
    # SFS (Seguro Familiar de Salud)
    sfs_employee_rate = fields.Float(
        string='SFS Empleado (%)',
        required=True,
        digits=(5, 2),
        default=3.04,
        help="Porcentaje de aporte del empleado a SFS (Plan Estatal)"
    )
    
    sfs_employer_rate = fields.Float(
        string='SFS Empleador (%)',
        required=True,
        digits=(5, 2),
        default=7.09,
        help="Porcentaje de aporte del empleador a SFS (Plan Estatal)"
    )
    
    # Infotep
    infotep_rate = fields.Float(
        string='Infotep (%)',
        required=True,
        digits=(5, 2),
        default=1.00,
        help="Porcentaje de aporte patronal a Infotep (sobre nómina total)"
    )
    
    # Totales calculados
    total_employee_rate = fields.Float(
        string='Total Empleado (%)',
        compute='_compute_total_rates',
        store=True,
        digits=(5, 2),
        help="Total de aportes del empleado"
    )
    
    total_employer_rate = fields.Float(
        string='Total Empleador (%)',
        compute='_compute_total_rates',
        store=True,
        digits=(5, 2),
        help="Total de aportes del empleador"
    )
    
    notes = fields.Text(
        string='Notas',
        help="Notas adicionales sobre esta configuración"
    )
    
    @api.depends('afp_employee_rate', 'ars_employee_rate', 'sfs_employee_rate',
                 'afp_employer_rate', 'ars_employer_rate', 'sfs_employer_rate', 'infotep_rate')
    def _compute_total_rates(self):
        for record in self:
            record.total_employee_rate = (
                record.afp_employee_rate +
                record.ars_employee_rate +
                record.sfs_employee_rate
            )
            record.total_employer_rate = (
                record.afp_employer_rate +
                record.ars_employer_rate +
                record.sfs_employer_rate +
                record.infotep_rate
            )
    
    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if record.date_to and record.date_from > record.date_to:
                raise ValidationError(_("La fecha 'Válido Desde' debe ser menor que 'Válido Hasta'"))
    
    @api.constrains('afp_employee_rate', 'afp_employer_rate', 'ars_employee_rate',
                    'ars_employer_rate', 'sfs_employee_rate', 'sfs_employer_rate', 'infotep_rate')
    def _check_rates(self):
        for record in self:
            rates = [
                record.afp_employee_rate, record.afp_employer_rate,
                record.ars_employee_rate, record.ars_employer_rate,
                record.sfs_employee_rate, record.sfs_employer_rate,
                record.infotep_rate
            ]
            if any(rate < 0 or rate > 100 for rate in rates):
                raise ValidationError(_("Los porcentajes deben estar entre 0 y 100"))
    
    @api.model
    def get_rates_for_date(self, date=None, company_id=None):
        """
        Obtiene las tasas TSS vigentes para una fecha determinada
        
        :param date: Fecha para la cual se buscan las tasas. Si es None, usa la fecha actual
        :param company_id: ID de la compañía. Si es None, usa la compañía actual
        :return: Recordset de tss.rate.config o False si no se encuentra
        """
        if not date:
            date = fields.Date.today()
        if not company_id:
            company_id = self.env.company.id
        
        domain = [
            ('company_id', '=', company_id),
            ('date_from', '<=', date),
            ('active', '=', True),
            '|',
            ('date_to', '>=', date),
            ('date_to', '=', False)
        ]
        
        return self.search(domain, order='date_from desc', limit=1)
    
    def name_get(self):
        result = []
        for record in self:
            if record.date_to:
                name = f"{record.name} ({record.date_from} - {record.date_to})"
            else:
                name = f"{record.name} (Desde {record.date_from})"
            result.append((record.id, name))
        return result

