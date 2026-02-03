# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    
    # Montos TSS
    tss_afp_employee = fields.Float(
        string='AFP Empleado',
        compute='_compute_tss_amounts',
        store=True,
        digits=(16, 2),
        help="Aporte del empleado a AFP"
    )
    
    tss_afp_employer = fields.Float(
        string='AFP Empleador',
        compute='_compute_tss_amounts',
        store=True,
        digits=(16, 2),
        help="Aporte del empleador a AFP"
    )
    
    tss_ars_employee = fields.Float(
        string='ARS Empleado',
        compute='_compute_tss_amounts',
        store=True,
        digits=(16, 2),
        help="Aporte del empleado a ARS"
    )
    
    tss_ars_employer = fields.Float(
        string='ARS Empleador',
        compute='_compute_tss_amounts',
        store=True,
        digits=(16, 2),
        help="Aporte del empleador a ARS"
    )
    
    tss_sfs_employee = fields.Float(
        string='SFS Empleado',
        compute='_compute_tss_amounts',
        store=True,
        digits=(16, 2),
        help="Aporte del empleado a SFS"
    )
    
    tss_sfs_employer = fields.Float(
        string='SFS Empleador',
        compute='_compute_tss_amounts',
        store=True,
        digits=(16, 2),
        help="Aporte del empleador a SFS"
    )
    
    tss_infotep = fields.Float(
        string='Infotep',
        compute='_compute_tss_amounts',
        store=True,
        digits=(16, 2),
        help="Aporte patronal a Infotep"
    )
    
    tss_total_employee = fields.Float(
        string='Total TSS Empleado',
        compute='_compute_tss_totals',
        store=True,
        digits=(16, 2),
        help="Total de aportes del empleado a TSS"
    )
    
    tss_total_employer = fields.Float(
        string='Total TSS Empleador',
        compute='_compute_tss_totals',
        store=True,
        digits=(16, 2),
        help="Total de aportes del empleador a TSS"
    )
    
    # Montos ISR
    isr_gross_salary = fields.Float(
        string='Salario Bruto ISR',
        compute='_compute_isr_amounts',
        store=True,
        digits=(16, 2),
        help="Salario bruto anual para ISR"
    )
    
    isr_deductions = fields.Float(
        string='Deducciones ISR',
        compute='_compute_isr_amounts',
        store=True,
        digits=(16, 2),
        help="Total de deducciones permitidas para ISR"
    )
    
    isr_taxable_salary = fields.Float(
        string='Salario Gravable ISR',
        compute='_compute_isr_amounts',
        store=True,
        digits=(16, 2),
        help="Salario anual gravable para ISR"
    )
    
    isr_annual = fields.Float(
        string='ISR Anual',
        compute='_compute_isr_amounts',
        store=True,
        digits=(16, 2),
        help="Impuesto sobre la renta anual"
    )
    
    isr_monthly = fields.Float(
        string='ISR Mensual',
        compute='_compute_isr_amounts',
        store=True,
        digits=(16, 2),
        help="Impuesto sobre la renta mensual"
    )
    
    # Prestaciones
    provision_cesantia = fields.Float(
        string='Provisión Cesantía',
        compute='_compute_provision_amounts',
        store=True,
        digits=(16, 2),
        help="Provisión mensual de cesantía"
    )
    
    provision_preaviso = fields.Float(
        string='Provisión Preaviso',
        compute='_compute_provision_amounts',
        store=True,
        digits=(16, 2),
        help="Provisión mensual de preaviso"
    )
    
    provision_vacaciones = fields.Float(
        string='Provisión Vacaciones',
        compute='_compute_provision_amounts',
        store=True,
        digits=(16, 2),
        help="Provisión mensual de vacaciones"
    )
    
    provision_salario_navidad = fields.Float(
        string='Provisión Salario Navidad',
        compute='_compute_provision_amounts',
        store=True,
        digits=(16, 2),
        help="Provisión mensual de salario de navidad"
    )
    
    provision_total = fields.Float(
        string='Total Provisiones',
        compute='_compute_provision_total',
        store=True,
        digits=(16, 2),
        help="Total de provisiones laborales"
    )
    
    @api.depends('line_ids', 'line_ids.total')
    def _compute_tss_amounts(self):
        """Calcula los montos individuales de TSS desde las líneas de nómina"""
        for payslip in self:
            payslip.tss_afp_employee = payslip._get_salary_line_total('AFP_EMPLOYEE')
            payslip.tss_afp_employer = payslip._get_salary_line_total('AFP_EMPLOYER')
            payslip.tss_ars_employee = payslip._get_salary_line_total('ARS_EMPLOYEE')
            payslip.tss_ars_employer = payslip._get_salary_line_total('ARS_EMPLOYER')
            payslip.tss_sfs_employee = payslip._get_salary_line_total('SFS_EMPLOYEE')
            payslip.tss_sfs_employer = payslip._get_salary_line_total('SFS_EMPLOYER')
            payslip.tss_infotep = payslip._get_salary_line_total('INFOTEP')
    
    @api.depends('tss_afp_employee', 'tss_ars_employee', 'tss_sfs_employee',
                 'tss_afp_employer', 'tss_ars_employer', 'tss_sfs_employer', 'tss_infotep')
    def _compute_tss_totals(self):
        """Calcula los totales de TSS"""
        for payslip in self:
            payslip.tss_total_employee = (
                abs(payslip.tss_afp_employee) +
                abs(payslip.tss_ars_employee) +
                abs(payslip.tss_sfs_employee)
            )
            payslip.tss_total_employer = (
                abs(payslip.tss_afp_employer) +
                abs(payslip.tss_ars_employer) +
                abs(payslip.tss_sfs_employer) +
                abs(payslip.tss_infotep)
            )
    
    @api.depends('line_ids', 'line_ids.total')
    def _compute_isr_amounts(self):
        """Calcula los montos de ISR desde las líneas de nómina"""
        for payslip in self:
            payslip.isr_gross_salary = payslip._get_salary_line_total('GROSS')
            payslip.isr_deductions = payslip._get_salary_line_total('ISR_DEDUCTIONS')
            payslip.isr_taxable_salary = payslip._get_salary_line_total('ISR_TAXABLE')
            payslip.isr_annual = payslip._get_salary_line_total('ISR_ANNUAL')
            payslip.isr_monthly = payslip._get_salary_line_total('ISR')
    
    @api.depends('line_ids', 'line_ids.total')
    def _compute_provision_amounts(self):
        """Calcula las provisiones desde las líneas de nómina"""
        for payslip in self:
            payslip.provision_cesantia = payslip._get_salary_line_total('PROVISION_CESANTIA')
            payslip.provision_preaviso = payslip._get_salary_line_total('PROVISION_PREAVISO')
            payslip.provision_vacaciones = payslip._get_salary_line_total('PROVISION_VACACIONES')
            payslip.provision_salario_navidad = payslip._get_salary_line_total('PROVISION_SALARIO_NAVIDAD')
    
    @api.depends('provision_cesantia', 'provision_preaviso', 'provision_vacaciones', 'provision_salario_navidad')
    def _compute_provision_total(self):
        """Calcula el total de provisiones"""
        for payslip in self:
            payslip.provision_total = (
                payslip.provision_cesantia +
                payslip.provision_preaviso +
                payslip.provision_vacaciones +
                payslip.provision_salario_navidad
            )
    
    def _get_salary_line_total(self, code):
        """
        Obtiene el total de una línea salarial por código
        
        :param code: Código de la regla salarial
        :return: Total de la línea o 0.0 si no existe
        """
        self.ensure_one()
        line = self.line_ids.filtered(lambda l: l.code == code)
        return line.total if line else 0.0

