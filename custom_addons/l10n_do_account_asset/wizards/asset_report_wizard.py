# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import base64
from io import BytesIO
try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None


class AssetReportWizard(models.TransientModel):
    _name = 'asset.report.wizard'
    _description = 'Asistente de Reportes de Activos'

    date_from = fields.Date(
        string='Desde',
        required=True,
        default=fields.Date.today().replace(day=1)
    )
    date_to = fields.Date(
        string='Hasta',
        required=True,
        default=fields.Date.context_today
    )
    category_ids = fields.Many2many(
        'account.asset.category',
        string='Categorías'
    )
    state = fields.Selection(
        [
            ('draft', 'Borrador'),
            ('running', 'En Uso'),
            ('close', 'Cerrado'),
            ('disposed', 'Dado de Baja'),
        ],
        string='Estado'
    )
    excel_file = fields.Binary(
        string='Archivo Excel',
        readonly=True
    )
    excel_filename = fields.Char(
        string='Nombre del Archivo',
        default='reporte_activos.xlsx'
    )
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company
    )

    def action_generate_report(self):
        """Genera reporte Excel de activos"""
        self.ensure_one()
        
        if not xlsxwriter:
            raise UserError(_('La biblioteca xlsxwriter no está instalada.'))
        
        # Construye dominio
        domain = [
            ('acquisition_date', '>=', self.date_from),
            ('acquisition_date', '<=', self.date_to),
            ('company_id', '=', self.company_id.id),
        ]
        if self.category_ids:
            domain.append(('category_id', 'in', self.category_ids.ids))
        if self.state:
            domain.append(('state', '=', self.state))
        
        assets = self.env['account.asset'].search(domain, order='acquisition_date, code')
        
        # Crea archivo Excel
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Activos Fijos')
        
        # Formatos
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#002D62',
            'font_color': 'white',
            'align': 'center',
            'border': 1
        })
        money_format = workbook.add_format({'num_format': '#,##0.00', 'border': 1})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy', 'border': 1})
        text_format = workbook.add_format({'border': 1})
        
        # Encabezados
        headers = [
            'Código', 'Nombre', 'Categoría', 'Fecha Adquisición',
            'Valor Compra', 'Valor Residual', 'Depreciación Acumulada',
            'Valor en Libros', 'Tasa %', 'Estado', 'Ubicación', 'NCF'
        ]
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
            worksheet.set_column(col, col, 15)
        
        # Datos
        row = 1
        for asset in assets:
            worksheet.write(row, 0, asset.code or '', text_format)
            worksheet.write(row, 1, asset.name or '', text_format)
            worksheet.write(row, 2, asset.category_id.name or '', text_format)
            worksheet.write(row, 3, asset.acquisition_date, date_format)
            worksheet.write(row, 4, asset.purchase_value, money_format)
            worksheet.write(row, 5, asset.salvage_value, money_format)
            worksheet.write(row, 6, asset.depreciated_value, money_format)
            worksheet.write(row, 7, asset.book_value, money_format)
            worksheet.write(row, 8, asset.depreciation_rate, text_format)
            worksheet.write(row, 9, dict(asset._fields['state'].selection).get(asset.state), text_format)
            worksheet.write(row, 10, asset.location or '', text_format)
            worksheet.write(row, 11, asset.l10n_do_ncf or '', text_format)
            row += 1
        
        workbook.close()
        excel_data = base64.b64encode(output.getvalue())
        output.close()
        
        self.write({
            'excel_file': excel_data,
            'excel_filename': f'activos_fijos_{self.date_from}_{self.date_to}.xlsx'
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'asset.report.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_download_excel(self):
        """Descarga el archivo Excel"""
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content?model=asset.report.wizard&id={self.id}&field=excel_file&filename_field=excel_filename&download=true',
            'target': 'self',
        }

