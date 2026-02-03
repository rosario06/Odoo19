# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
from io import BytesIO
try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None


class IT1Wizard(models.TransientModel):
    _name = 'it1.wizard'
    _description = 'Asistente Formulario IT-1'
    
    year = fields.Selection(
        selection='_get_years',
        string='Año Fiscal',
        required=True,
        default=lambda self: str(fields.Date.today().year)
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company
    )
    
    # Filtros opcionales
    employee_ids = fields.Many2many(
        'hr.employee',
        string='Empleados',
        help="Dejar vacío para incluir todos los empleados"
    )
    
    report_format = fields.Selection([
        ('excel', 'Excel (IT-1)'),
        ('pdf', 'Certificación PDF')
    ], string='Formato', default='excel', required=True)
    
    # Resultado
    excel_file = fields.Binary(
        string='Archivo',
        readonly=True
    )
    
    excel_filename = fields.Char(
        string='Nombre Archivo',
        readonly=True
    )
    
    @api.model
    def _get_years(self):
        """Retorna los últimos 5 años"""
        current_year = fields.Date.today().year
        return [(str(year), str(year)) for year in range(current_year - 4, current_year + 1)]
    
    def action_generate_it1(self):
        """Genera el formulario IT-1"""
        self.ensure_one()
        
        if self.report_format == 'excel':
            return self._generate_it1_excel()
        else:
            return self._generate_certificate_pdf()
    
    def _get_isr_data(self):
        """Obtiene los datos de ISR para el año fiscal"""
        self.ensure_one()
        
        year = int(self.year)
        date_from = fields.Date.from_string(f"{year}-01-01")
        date_to = fields.Date.from_string(f"{year}-12-31")
        
        domain = [
            ('date', '>=', date_from),
            ('date', '<=', date_to),
            ('company_id', '=', self.company_id.id),
            ('state', 'in', ['confirmed', 'reported'])
        ]
        
        if self.employee_ids:
            domain.append(('employee_id', 'in', self.employee_ids.ids))
        
        return self.env['isr.payroll'].search(domain, order='employee_id, date')
    
    def _aggregate_employee_data(self, isr_records):
        """Agrupa los datos de ISR por empleado"""
        employee_data = {}
        
        for record in isr_records:
            emp_id = record.employee_id.id
            if emp_id not in employee_data:
                employee_data[emp_id] = {
                    'employee': record.employee_id,
                    'cedula': record.employee_id.cedula or '',
                    'rnc': record.employee_id.rnc or '',
                    'total_salary': 0.0,
                    'total_tss': 0.0,
                    'total_dependents_deduction': 0.0,
                    'total_other_deductions': 0.0,
                    'total_deductions': 0.0,
                    'taxable_income': 0.0,
                    'total_isr': 0.0,
                    'months': []
                }
            
            employee_data[emp_id]['total_salary'] += record.monthly_salary
            employee_data[emp_id]['total_tss'] += record.tss_deductions
            employee_data[emp_id]['total_dependents_deduction'] = record.dependents_deduction  # Anual
            employee_data[emp_id]['total_other_deductions'] = record.other_deductions  # Anual
            employee_data[emp_id]['total_deductions'] = record.total_deductions  # Anual
            employee_data[emp_id]['taxable_income'] = record.taxable_income  # Anual
            employee_data[emp_id]['total_isr'] += record.isr_monthly
            employee_data[emp_id]['months'].append(record.date.month)
        
        return employee_data
    
    def _generate_it1_excel(self):
        """Genera el formulario IT-1 en Excel"""
        self.ensure_one()
        
        if not xlsxwriter:
            raise UserError(_("La librería 'xlsxwriter' no está instalada. Por favor instálela con: pip install xlsxwriter"))
        
        isr_records = self._get_isr_data()
        
        if not isr_records:
            raise UserError(_("No se encontraron registros de ISR para el año seleccionado"))
        
        employee_data = self._aggregate_employee_data(isr_records)
        
        # Crear archivo Excel
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('IT-1')
        
        # Formatos
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#1976D2',
            'font_color': 'white',
            'border': 1,
            'align': 'center'
        })
        
        money_format = workbook.add_format({'num_format': '#,##0.00'})
        total_format = workbook.add_format({'bold': True, 'num_format': '#,##0.00', 'bg_color': '#E3F2FD'})
        
        # Título
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'center'
        })
        worksheet.merge_range('A1:L1', f'FORMULARIO IT-1 - AÑO FISCAL {self.year}', title_format)
        worksheet.merge_range('A2:L2', self.company_id.name, title_format)
        worksheet.write('A3', f'RNC: {self.company_id.vat or "N/A"}')
        
        # Encabezados (fila 5)
        headers = [
            'Empleado', 'Cédula', 'RNC',
            'Ingresos Brutos', 'Deducciones TSS',
            'Deducción Dependientes', 'Otras Deducciones',
            'Total Deducciones', 'Renta Gravable',
            'ISR Retenido', 'Meses Trabajados', 'Salario Promedio'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(4, col, header, header_format)
        
        # Datos
        row = 5
        for emp_id, data in employee_data.items():
            months_worked = len(data['months'])
            avg_salary = data['total_salary'] / months_worked if months_worked > 0 else 0
            
            worksheet.write(row, 0, data['employee'].name)
            worksheet.write(row, 1, data['cedula'])
            worksheet.write(row, 2, data['rnc'])
            worksheet.write(row, 3, data['total_salary'], money_format)
            worksheet.write(row, 4, data['total_tss'] * 12, money_format)  # TSS anual
            worksheet.write(row, 5, data['total_dependents_deduction'], money_format)
            worksheet.write(row, 6, data['total_other_deductions'], money_format)
            worksheet.write(row, 7, data['total_deductions'], money_format)
            worksheet.write(row, 8, data['taxable_income'], money_format)
            worksheet.write(row, 9, data['total_isr'], money_format)
            worksheet.write(row, 10, months_worked)
            worksheet.write(row, 11, avg_salary, money_format)
            row += 1
        
        # Totales
        worksheet.write(row, 2, 'TOTALES:', total_format)
        worksheet.write_formula(row, 3, f'=SUM(D6:D{row})', total_format)
        worksheet.write_formula(row, 4, f'=SUM(E6:E{row})', total_format)
        worksheet.write_formula(row, 5, f'=SUM(F6:F{row})', total_format)
        worksheet.write_formula(row, 6, f'=SUM(G6:G{row})', total_format)
        worksheet.write_formula(row, 7, f'=SUM(H6:H{row})', total_format)
        worksheet.write_formula(row, 8, f'=SUM(I6:I{row})', total_format)
        worksheet.write_formula(row, 9, f'=SUM(J6:J{row})', total_format)
        
        # Ajustar ancho de columnas
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:C', 15)
        worksheet.set_column('D:L', 18)
        
        workbook.close()
        
        # Guardar archivo
        excel_data = output.getvalue()
        filename = f"IT1_{self.company_id.vat or 'SIN_RNC'}_{self.year}.xlsx"
        
        self.write({
            'excel_file': base64.b64encode(excel_data),
            'excel_filename': filename
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'it1.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
    
    def _generate_certificate_pdf(self):
        """Genera certificación de ingresos en PDF"""
        self.ensure_one()
        
        isr_records = self._get_isr_data()
        
        if not isr_records:
            raise UserError(_("No se encontraron registros de ISR para el año seleccionado"))
        
        # Por ahora, retornamos la misma vista de wizard
        # TODO: Implementar generación de PDF
        raise UserError(_("La generación de certificación PDF estará disponible próximamente"))
    
    def action_download_file(self):
        """Descarga el archivo generado"""
        self.ensure_one()
        
        if not self.excel_file:
            raise UserError(_("Primero debe generar el reporte"))
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/?model=it1.wizard&id={self.id}&field=excel_file&filename_field=excel_filename&download=true',
            'target': 'self',
        }

