# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
from io import BytesIO
try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None


class L10nDoInventoryReportWizard(models.TransientModel):
    _name = 'l10n.do.inventory.report.wizard'
    _description = 'Asistente de Reporte de Inventario DGII'
    
    date = fields.Date(
        string='Fecha de Corte',
        required=True,
        default=fields.Date.today,
        help="Fecha para la cual se calculará el inventario"
    )
    
    location_ids = fields.Many2many(
        'stock.location',
        string='Ubicaciones',
        domain="[('usage', '=', 'internal')]",
        required=True,
        help="Ubicaciones a incluir en el reporte"
    )
    
    category_ids = fields.Many2many(
        'product.category',
        string='Categorías de Productos',
        help="Dejar vacío para incluir todas las categorías"
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company
    )
    
    include_zero_qty = fields.Boolean(
        string='Incluir Productos sin Existencia',
        default=False
    )
    
    valuation = fields.Boolean(
        string='Incluir Valorización',
        default=True
    )
    
    # Campos para descarga
    excel_file = fields.Binary(
        string='Archivo Excel',
        readonly=True
    )
    
    excel_filename = fields.Char(
        string='Nombre del Archivo',
        readonly=True
    )
    
    def action_generate_report(self):
        """Generar el reporte de inventario"""
        self.ensure_one()
        
        # Obtener datos de inventario
        inventory_data = self._get_inventory_data()
        
        if not inventory_data:
            raise UserError(_('No se encontraron productos en las ubicaciones seleccionadas.'))
        
        # Generar Excel
        return self._generate_excel(inventory_data)
    
    def _get_inventory_data(self):
        """Obtener datos de inventario"""
        Product = self.env['product.product']
        StockQuant = self.env['stock.quant']
        
        # Construir dominio para productos
        product_domain = [('type', '=', 'product')]
        
        if self.category_ids:
            product_domain.append(('categ_id', 'in', self.category_ids.ids))
        
        products = Product.search(product_domain)
        
        inventory_data = []
        
        for product in products:
            # Obtener cantidad en ubicaciones
            quants = StockQuant.search([
                ('product_id', '=', product.id),
                ('location_id', 'in', self.location_ids.ids),
                ('company_id', '=', self.company_id.id),
            ])
            
            total_qty = sum(quants.mapped('quantity'))
            
            if total_qty > 0 or self.include_zero_qty:
                # Calcular valor
                if self.valuation:
                    unit_cost = product.standard_price
                    total_value = total_qty * unit_cost
                else:
                    unit_cost = 0.0
                    total_value = 0.0
                
                inventory_data.append({
                    'code': product.default_code or '',
                    'name': product.name,
                    'category': product.categ_id.name,
                    'uom': product.uom_id.name,
                    'quantity': total_qty,
                    'unit_cost': unit_cost,
                    'total_value': total_value,
                    'tax_classification': dict(product._fields['l10n_do_tax_classification'].selection).get(
                        product.l10n_do_tax_classification, ''
                    ),
                    'tariff_code': product.l10n_do_tariff_code or '',
                })
        
        return sorted(inventory_data, key=lambda x: (x['category'], x['name']))
    
    def _generate_excel(self, inventory_data):
        """Generar reporte en Excel"""
        if not xlsxwriter:
            raise UserError(_('La librería xlsxwriter no está instalada. Por favor, instálela con: pip install xlsxwriter'))
        
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Inventario')
        
        # Formatos
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#002D62',
            'font_color': 'white',
            'border': 1
        })
        
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#ED1C24',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        number_format = workbook.add_format({'num_format': '#,##0.00', 'border': 1})
        text_format = workbook.add_format({'border': 1})
        currency_format = workbook.add_format({'num_format': '$#,##0.00', 'border': 1})
        
        # Título
        worksheet.merge_range('A1:H1', f'REPORTE DE INVENTARIO - {self.company_id.name}', title_format)
        worksheet.merge_range('A2:H2', f'Fecha de Corte: {self.date.strftime("%d/%m/%Y")}', text_format)
        
        # Cabeceras
        row = 3
        headers = ['Código', 'Descripción', 'Categoría', 'UM', 'Cantidad', 'Costo Unit.', 'Valor Total', 'Clasificación Fiscal']
        for col, header in enumerate(headers):
            worksheet.write(row, col, header, header_format)
        
        # Datos
        row += 1
        total_value = 0.0
        
        for item in inventory_data:
            worksheet.write(row, 0, item['code'], text_format)
            worksheet.write(row, 1, item['name'], text_format)
            worksheet.write(row, 2, item['category'], text_format)
            worksheet.write(row, 3, item['uom'], text_format)
            worksheet.write(row, 4, item['quantity'], number_format)
            worksheet.write(row, 5, item['unit_cost'], currency_format)
            worksheet.write(row, 6, item['total_value'], currency_format)
            worksheet.write(row, 7, item['tax_classification'], text_format)
            
            total_value += item['total_value']
            row += 1
        
        # Total
        worksheet.write(row, 5, 'TOTAL:', header_format)
        worksheet.write(row, 6, total_value, currency_format)
        
        # Ajustar anchos
        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:B', 40)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 8)
        worksheet.set_column('E:H', 15)
        
        workbook.close()
        output.seek(0)
        
        # Guardar en el wizard
        filename = f'Inventario_{self.date.strftime("%Y%m%d")}.xlsx'
        self.write({
            'excel_file': base64.b64encode(output.read()),
            'excel_filename': filename,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'l10n.do.inventory.report.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'show_download': True},
        }
    
    def action_download_excel(self):
        """Descargar el archivo Excel"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content?model=l10n.do.inventory.report.wizard&id={self.id}&field=excel_file&filename={self.excel_filename}&download=true',
            'target': 'self',
        }

