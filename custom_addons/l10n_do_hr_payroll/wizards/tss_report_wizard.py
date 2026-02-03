# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
from io import BytesIO
try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None


class TSSReportWizard(models.TransientModel):
    _name = 'tss.report.wizard'
    _description = 'Asistente Reporte TSS'
    
    date_from = fields.Date(
        string='Desde',
        required=True,
        default=lambda self: fields.Date.today().replace(day=1)
    )
    
    date_to = fields.Date(
        string='Hasta',
        required=True,
        default=fields.Date.today
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company
    )
    
    report_type = fields.Selection([
        ('summary', 'Resumen Mensual'),
        ('detailed', 'Detallado por Empleado'),
        ('excel', 'Exportar a Excel')
    ], string='Tipo de Reporte', default='detailed', required=True)
    
    # Filtros opcionales
    employee_ids = fields.Many2many(
        'hr.employee',
        string='Empleados',
        help="Dejar vacío para incluir todos los empleados"
    )
    
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('reported', 'Reportado')
    ], string='Estado', help="Filtrar por estado de aportes")
    
    # Resultado
    excel_file = fields.Binary(
        string='Archivo Excel',
        readonly=True
    )
    
    excel_filename = fields.Char(
        string='Nombre Archivo',
        readonly=True
    )
    
    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for wizard in self:
            if wizard.date_from > wizard.date_to:
                raise UserError(_("La fecha 'Desde' debe ser menor o igual a la fecha 'Hasta'"))
    
    def action_generate_report(self):
        """Genera el reporte según el tipo seleccionado"""
        self.ensure_one()
        
        if self.report_type == 'excel':
            return self._generate_excel_report()
        elif self.report_type == 'summary':
            return self._generate_summary_report()
        else:
            return self._generate_detailed_report()
    
    def _get_tss_contributions(self):
        """Obtiene los aportes TSS según los filtros"""
        self.ensure_one()
        
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('company_id', '=', self.company_id.id)
        ]
        
        if self.employee_ids:
            domain.append(('employee_id', 'in', self.employee_ids.ids))
        
        if self.state:
            domain.append(('state', '=', self.state))
        
        return self.env['tss.contribution'].search(domain, order='employee_id, date')
    
    def _generate_summary_report(self):
        """Genera reporte resumen"""
        self.ensure_one()
        
        contributions = self._get_tss_contributions()
        
        if not contributions:
            raise UserError(_("No se encontraron aportes TSS para el período seleccionado"))
        
        # Calcular totales
        total_employees = len(contributions.mapped('employee_id'))
        total_base_salary = sum(contributions.mapped('base_salary'))
        total_employee_contrib = sum(contributions.mapped('total_employee'))
        total_employer_contrib = sum(contributions.mapped('total_employer'))
        total_tss = sum(contributions.mapped('total_tss'))
        
        # Retornar acción para mostrar reporte
        return {
            'type': 'ir.actions.act_window',
            'name': 'Resumen Aportes TSS',
            'res_model': 'tss.contribution',
            'view_mode': 'list',
            'domain': [('id', 'in', contributions.ids)],
            'context': {
                'search_default_group_employee': 1,
                'tss_summary': {
                    'employees': total_employees,
                    'base_salary': total_base_salary,
                    'employee_contrib': total_employee_contrib,
                    'employer_contrib': total_employer_contrib,
                    'total_tss': total_tss
                }
            }
        }
    
    def _generate_detailed_report(self):
        """Genera reporte detallado"""
        self.ensure_one()
        
        contributions = self._get_tss_contributions()
        
        if not contributions:
            raise UserError(_("No se encontraron aportes TSS para el período seleccionado"))
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Aportes TSS Detallado',
            'res_model': 'tss.contribution',
            'view_mode': 'list,form',
            'domain': [('id', 'in', contributions.ids)],
            'context': {'search_default_group_period': 1}
        }
    
    def _generate_excel_report(self):
        """Genera reporte en Excel"""
        self.ensure_one()
        
        if not xlsxwriter:
            raise UserError(_("La librería 'xlsxwriter' no está instalada. Por favor instálela con: pip install xlsxwriter"))
        
        contributions = self._get_tss_contributions()
        
        if not contributions:
            raise UserError(_("No se encontraron aportes TSS para el período seleccionado"))
        
        # Crear archivo Excel
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Aportes TSS')
        
        # Formatos
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4CAF50',
            'font_color': 'white',
            'border': 1
        })
        
        money_format = workbook.add_format({'num_format': '#,##0.00'})
        total_format = workbook.add_format({'bold': True, 'num_format': '#,##0.00', 'bg_color': '#E8F5E9'})
        
        # Encabezados
        headers = [
            'Período', 'Empleado', 'TSS #', 'AFP #', 'ARS #', 'ARS Proveedor',
            'Salario Base', 'AFP Empleado', 'ARS Empleado', 'SFS Empleado', 'Total Empleado',
            'AFP Empleador', 'ARS Empleador', 'SFS Empleador', 'Infotep', 'Total Empleador',
            'Total TSS', 'Estado'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Datos
        row = 1
        for contrib in contributions:
            worksheet.write(row, 0, contrib.period or '')
            worksheet.write(row, 1, contrib.employee_id.name or '')
            worksheet.write(row, 2, contrib.tss_number or '')
            worksheet.write(row, 3, contrib.afp_number or '')
            worksheet.write(row, 4, contrib.ars_number or '')
            worksheet.write(row, 5, contrib.ars_provider or '')
            worksheet.write(row, 6, contrib.base_salary, money_format)
            worksheet.write(row, 7, contrib.afp_employee, money_format)
            worksheet.write(row, 8, contrib.ars_employee, money_format)
            worksheet.write(row, 9, contrib.sfs_employee, money_format)
            worksheet.write(row, 10, contrib.total_employee, money_format)
            worksheet.write(row, 11, contrib.afp_employer, money_format)
            worksheet.write(row, 12, contrib.ars_employer, money_format)
            worksheet.write(row, 13, contrib.sfs_employer, money_format)
            worksheet.write(row, 14, contrib.infotep, money_format)
            worksheet.write(row, 15, contrib.total_employer, money_format)
            worksheet.write(row, 16, contrib.total_tss, money_format)
            worksheet.write(row, 17, dict(contrib._fields['state'].selection).get(contrib.state, ''))
            row += 1
        
        # Totales
        worksheet.write(row, 5, 'TOTALES:', total_format)
        worksheet.write_formula(row, 6, f'=SUM(G2:G{row})', total_format)
        worksheet.write_formula(row, 7, f'=SUM(H2:H{row})', total_format)
        worksheet.write_formula(row, 8, f'=SUM(I2:I{row})', total_format)
        worksheet.write_formula(row, 9, f'=SUM(J2:J{row})', total_format)
        worksheet.write_formula(row, 10, f'=SUM(K2:K{row})', total_format)
        worksheet.write_formula(row, 11, f'=SUM(L2:L{row})', total_format)
        worksheet.write_formula(row, 12, f'=SUM(M2:M{row})', total_format)
        worksheet.write_formula(row, 13, f'=SUM(N2:N{row})', total_format)
        worksheet.write_formula(row, 14, f'=SUM(O2:O{row})', total_format)
        worksheet.write_formula(row, 15, f'=SUM(P2:P{row})', total_format)
        worksheet.write_formula(row, 16, f'=SUM(Q2:Q{row})', total_format)
        
        # Ajustar ancho de columnas
        worksheet.set_column('A:A', 12)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('C:F', 15)
        worksheet.set_column('G:Q', 14)
        worksheet.set_column('R:R', 12)
        
        workbook.close()
        
        # Guardar archivo
        excel_data = output.getvalue()
        filename = f"Reporte_TSS_{self.date_from.strftime('%Y%m')}_{self.date_to.strftime('%Y%m')}.xlsx"
        
        self.write({
            'excel_file': base64.b64encode(excel_data),
            'excel_filename': filename
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'tss.report.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
    
    def action_download_excel(self):
        """Descarga el archivo Excel generado"""
        self.ensure_one()
        
        if not self.excel_file:
            raise UserError(_("Primero debe generar el reporte Excel"))
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/?model=tss.report.wizard&id={self.id}&field=excel_file&filename_field=excel_filename&download=true',
            'target': 'self',
        }

