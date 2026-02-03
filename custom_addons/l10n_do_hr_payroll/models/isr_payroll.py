# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ISRPayroll(models.Model):
    _name = 'isr.payroll'
    _description = 'Retención ISR de Nómina'
    _order = 'date desc, employee_id'
    
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
        index=True
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        default=lambda self: self.env.company,
        required=True,
        readonly=True
    )
    
    date = fields.Date(
        string='Fecha',
        required=True,
        default=fields.Date.today,
        readonly=True,
        index=True
    )
    
    period = fields.Char(
        string='Período',
        compute='_compute_period',
        store=True,
        help="Formato: YYYY-MM"
    )
    
    # Salarios
    monthly_salary = fields.Float(
        string='Salario Mensual',
        digits=(16, 2),
        required=True,
        help="Salario bruto mensual"
    )
    
    annual_salary = fields.Float(
        string='Salario Anual',
        compute='_compute_annual_salary',
        store=True,
        digits=(16, 2),
        help="Salario mensual * 12"
    )
    
    # Deducciones
    tss_deductions = fields.Float(
        string='Deducciones TSS',
        digits=(16, 2),
        help="Aportes TSS del empleado (AFP + ARS + SFS)"
    )
    
    dependents = fields.Integer(
        string='Dependientes',
        default=0,
        help="Número de dependientes para deducción"
    )
    
    dependents_deduction = fields.Float(
        string='Deducción Dependientes',
        compute='_compute_dependents_deduction',
        store=True,
        digits=(16, 2),
        help="Deducción anual por dependientes"
    )
    
    other_deductions = fields.Float(
        string='Otras Deducciones',
        digits=(16, 2),
        default=0.0,
        help="Otras deducciones permitidas (educación, seguros, etc.)"
    )
    
    total_deductions = fields.Float(
        string='Total Deducciones',
        compute='_compute_total_deductions',
        store=True,
        digits=(16, 2),
        help="Suma de todas las deducciones anuales"
    )
    
    # Base imponible
    taxable_income = fields.Float(
        string='Renta Gravable',
        compute='_compute_taxable_income',
        store=True,
        digits=(16, 2),
        help="Salario anual - deducciones"
    )
    
    # ISR
    isr_annual = fields.Float(
        string='ISR Anual',
        compute='_compute_isr',
        store=True,
        digits=(16, 2),
        help="Impuesto sobre la renta anual calculado"
    )
    
    isr_monthly = fields.Float(
        string='ISR Mensual',
        compute='_compute_isr',
        store=True,
        digits=(16, 2),
        help="ISR anual / 12"
    )
    
    # Detalles del cálculo
    bracket_applied = fields.Char(
        string='Tramo Aplicado',
        help="Nombre del tramo de ISR aplicado"
    )
    
    effective_rate = fields.Float(
        string='Tasa Efectiva (%)',
        compute='_compute_effective_rate',
        store=True,
        digits=(5, 2),
        help="(ISR Anual / Salario Anual) * 100"
    )
    
    # Relaciones
    payslip_id = fields.Many2one(
        'hr.payslip',
        string='Nómina',
        readonly=True,
        ondelete='cascade',
        help="Nómina desde la cual se generó esta retención"
    )
    
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('reported', 'Reportado')
    ], string='Estado', default='draft', readonly=True)
    
    notes = fields.Text(
        string='Notas'
    )
    
    @api.depends('date')
    def _compute_period(self):
        for record in self:
            if record.date:
                record.period = record.date.strftime('%Y-%m')
            else:
                record.period = False
    
    @api.depends('monthly_salary')
    def _compute_annual_salary(self):
        for record in self:
            record.annual_salary = record.monthly_salary * 12
    
    @api.depends('dependents')
    def _compute_dependents_deduction(self):
        """
        Deducción por dependientes según normativa RD
        Aproximadamente RD$ 31,848.00 por dependiente al año (2024)
        """
        for record in self:
            # Máximo 3 dependientes
            valid_dependents = min(record.dependents, 3)
            deduction_per_dependent = 31848.00  # Valor aproximado 2024
            record.dependents_deduction = valid_dependents * deduction_per_dependent
    
    @api.depends('annual_salary', 'tss_deductions', 'dependents_deduction', 'other_deductions')
    def _compute_total_deductions(self):
        for record in self:
            # TSS anual = TSS mensual * 12
            tss_annual = record.tss_deductions * 12
            record.total_deductions = (
                tss_annual +
                record.dependents_deduction +
                record.other_deductions
            )
    
    @api.depends('annual_salary', 'total_deductions')
    def _compute_taxable_income(self):
        for record in self:
            record.taxable_income = max(0, record.annual_salary - record.total_deductions)
    
    @api.depends('taxable_income', 'date')
    def _compute_isr(self):
        """Calcula el ISR usando los tramos configurados"""
        for record in self:
            if record.taxable_income <= 0:
                record.isr_annual = 0.0
                record.isr_monthly = 0.0
                record.bracket_applied = 'Exento'
                continue
            
            # Obtener tramos ISR vigentes para la fecha
            ISRBracket = self.env['isr.tax.bracket']
            result = ISRBracket.calculate_isr(
                annual_salary=record.taxable_income,
                date=record.date,
                company_id=record.company_id.id
            )
            
            record.isr_annual = result.get('total_isr', 0.0)
            record.isr_monthly = result.get('monthly_isr', 0.0)
            
            # Determinar el tramo aplicado
            brackets_applied = result.get('brackets_applied', [])
            if brackets_applied:
                last_bracket = brackets_applied[-1]
                record.bracket_applied = last_bracket.get('bracket_name', 'N/A')
            else:
                record.bracket_applied = 'Exento'
    
    @api.depends('isr_annual', 'annual_salary')
    def _compute_effective_rate(self):
        for record in self:
            if record.annual_salary > 0:
                record.effective_rate = (record.isr_annual / record.annual_salary) * 100
            else:
                record.effective_rate = 0.0
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('isr.payroll') or 'New'
        return super().create(vals_list)
    
    def action_confirm(self):
        """Confirma la retención ISR"""
        self.write({'state': 'confirmed'})
    
    def action_report(self):
        """Marca como reportado a DGII"""
        self.write({'state': 'reported'})
    
    def action_draft(self):
        """Vuelve a borrador"""
        self.write({'state': 'draft'})
    
    @api.model
    def create_from_payslip(self, payslip):
        """
        Crea un registro de retención ISR desde una nómina
        
        :param payslip: Recordset de hr.payslip
        :return: Recordset de isr.payroll creado
        """
        if not payslip:
            return self.env['isr.payroll']
        
        contract = payslip.contract_id
        
        # Calcular deducciones TSS mensuales
        tss_deductions = (
            abs(payslip.tss_afp_employee) +
            abs(payslip.tss_ars_employee) +
            abs(payslip.tss_sfs_employee)
        )
        
        vals = {
            'name': f"ISR-{payslip.employee_id.name}-{payslip.date_from.strftime('%Y-%m')}",
            'employee_id': payslip.employee_id.id,
            'company_id': payslip.company_id.id,
            'date': payslip.date_from,
            'monthly_salary': contract.wage if contract else 0.0,
            'tss_deductions': tss_deductions,
            'dependents': contract.isr_dependents if contract else 0,
            'other_deductions': contract.isr_other_deductions if contract else 0.0,
            'payslip_id': payslip.id,
            'state': 'draft'
        }
        
        return self.create(vals)

