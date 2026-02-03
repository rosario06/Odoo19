# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TSSContribution(models.Model):
    _name = 'tss.contribution'
    _description = 'Aportes TSS Mensuales'
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
    base_salary = fields.Float(
        string='Salario Base',
        digits=(16, 2),
        required=True
    )
    
    taxable_salary_afp = fields.Float(
        string='Salario Cotizable AFP',
        digits=(16, 2),
        help="Salario con tope aplicado para AFP"
    )
    
    taxable_salary_ars = fields.Float(
        string='Salario Cotizable ARS',
        digits=(16, 2),
        help="Salario con tope aplicado para ARS"
    )
    
    taxable_salary_sfs = fields.Float(
        string='Salario Cotizable SFS',
        digits=(16, 2),
        help="Salario con tope aplicado para SFS"
    )
    
    # Aportes Empleado
    afp_employee = fields.Float(
        string='AFP Empleado',
        digits=(16, 2),
        required=True
    )
    
    ars_employee = fields.Float(
        string='ARS Empleado',
        digits=(16, 2),
        required=True
    )
    
    sfs_employee = fields.Float(
        string='SFS Empleado',
        digits=(16, 2),
        required=True
    )
    
    total_employee = fields.Float(
        string='Total Empleado',
        compute='_compute_totals',
        store=True,
        digits=(16, 2)
    )
    
    # Aportes Empleador
    afp_employer = fields.Float(
        string='AFP Empleador',
        digits=(16, 2),
        required=True
    )
    
    ars_employer = fields.Float(
        string='ARS Empleador',
        digits=(16, 2),
        required=True
    )
    
    sfs_employer = fields.Float(
        string='SFS Empleador',
        digits=(16, 2),
        required=True
    )
    
    infotep = fields.Float(
        string='Infotep',
        digits=(16, 2),
        required=True
    )
    
    total_employer = fields.Float(
        string='Total Empleador',
        compute='_compute_totals',
        store=True,
        digits=(16, 2)
    )
    
    # Total
    total_tss = fields.Float(
        string='Total TSS',
        compute='_compute_totals',
        store=True,
        digits=(16, 2),
        help="Suma de aportes empleado + empleador"
    )
    
    # Información TSS del empleado
    tss_number = fields.Char(
        string='Número TSS',
        related='employee_id.tss_number',
        readonly=True
    )
    
    afp_number = fields.Char(
        string='Número AFP',
        help="Número de afiliación AFP del empleado"
    )
    
    ars_number = fields.Char(
        string='Número ARS',
        help="Número de afiliación ARS del empleado"
    )
    
    ars_provider = fields.Char(
        string='ARS Proveedor',
        help="Nombre de la ARS del empleado"
    )
    
    payslip_id = fields.Many2one(
        'hr.payslip',
        string='Nómina',
        readonly=True,
        ondelete='cascade',
        help="Nómina desde la cual se generó este aporte"
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
    
    @api.depends('afp_employee', 'ars_employee', 'sfs_employee',
                 'afp_employer', 'ars_employer', 'sfs_employer', 'infotep')
    def _compute_totals(self):
        for record in self:
            record.total_employee = (
                record.afp_employee +
                record.ars_employee +
                record.sfs_employee
            )
            record.total_employer = (
                record.afp_employer +
                record.ars_employer +
                record.sfs_employer +
                record.infotep
            )
            record.total_tss = record.total_employee + record.total_employer
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('tss.contribution') or 'New'
        return super().create(vals_list)
    
    def action_confirm(self):
        """Confirma el aporte TSS"""
        self.write({'state': 'confirmed'})
    
    def action_report(self):
        """Marca como reportado a TSS"""
        self.write({'state': 'reported'})
    
    def action_draft(self):
        """Vuelve a borrador"""
        self.write({'state': 'draft'})
    
    @api.model
    def create_from_payslip(self, payslip):
        """
        Crea un registro de aporte TSS desde una nómina
        
        :param payslip: Recordset de hr.payslip
        :return: Recordset de tss.contribution creado
        """
        if not payslip:
            return self.env['tss.contribution']
        
        contract = payslip.contract_id
        
        vals = {
            'name': f"TSS-{payslip.employee_id.name}-{payslip.date_from.strftime('%Y-%m')}",
            'employee_id': payslip.employee_id.id,
            'company_id': payslip.company_id.id,
            'date': payslip.date_from,
            'base_salary': contract.wage if contract else 0.0,
            'taxable_salary_afp': contract.wage if contract else 0.0,
            'taxable_salary_ars': contract.wage if contract else 0.0,
            'taxable_salary_sfs': contract.wage if contract else 0.0,
            'afp_employee': abs(payslip.tss_afp_employee),
            'ars_employee': abs(payslip.tss_ars_employee),
            'sfs_employee': abs(payslip.tss_sfs_employee),
            'afp_employer': abs(payslip.tss_afp_employer),
            'ars_employer': abs(payslip.tss_ars_employer),
            'sfs_employer': abs(payslip.tss_sfs_employer),
            'infotep': abs(payslip.tss_infotep),
            'afp_number': contract.afp_number if contract else False,
            'ars_number': contract.ars_number if contract else False,
            'ars_provider': contract.ars_provider if contract else False,
            'payslip_id': payslip.id,
            'state': 'draft'
        }
        
        return self.create(vals)

