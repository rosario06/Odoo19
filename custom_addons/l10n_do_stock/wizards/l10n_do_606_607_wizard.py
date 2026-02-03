# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
from io import BytesIO
try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None


class L10nDo606607Wizard(models.TransientModel):
    _name = 'l10n.do.606.607.wizard'
    _description = 'Asistente de Reportes 606/607 para Inventario'
    
    report_type = fields.Selection([
        ('606', 'Reporte 606 (Compras)'),
        ('607', 'Reporte 607 (Ventas)')
    ], string='Tipo de Reporte', required=True, default='607')
    
    date_from = fields.Date(
        string='Fecha Desde',
        required=True,
        default=lambda self: fields.Date.today().replace(day=1)
    )
    
    date_to = fields.Date(
        string='Fecha Hasta',
        required=True,
        default=fields.Date.today
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company
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
        """Generar el reporte 606/607"""
        self.ensure_one()
        
        if self.date_from > self.date_to:
            raise UserError(_('La fecha inicial no puede ser mayor que la fecha final.'))
        
        # Obtener datos según tipo de reporte
        if self.report_type == '606':
            report_data = self._get_606_data()
        else:
            report_data = self._get_607_data()
        
        if not report_data:
            raise UserError(_('No se encontraron movimientos de inventario para el período seleccionado.'))
        
        # Generar Excel
        return self._generate_excel(report_data)
    
    def _get_606_data(self):
        """Obtener datos para reporte 606 (Compras)"""
        StockPicking = self.env['stock.picking']
        
        # Buscar recepciones (incoming)
        domain = [
            ('picking_type_code', '=', 'incoming'),
            ('state', '=', 'done'),
            ('date_done', '>=', fields.Datetime.combine(self.date_from, fields.Datetime.min.time())),
            ('date_done', '<=', fields.Datetime.combine(self.date_to, fields.Datetime.max.time())),
            ('company_id', '=', self.company_id.id),
        ]
        
        pickings = StockPicking.search(domain)
        
        report_data = []
        
        for picking in pickings:
            if not picking.partner_id:
                continue
            
            # Calcular totales
            subtotal = 0.0
            itbis = 0.0
            
            for move in picking.move_ids:
                move_subtotal = move.product_uom_qty * move.price_unit
                move_itbis = move.l10n_do_itbis_amount or 0.0
                
                subtotal += move_subtotal
                itbis += move_itbis
            
            total = subtotal + itbis
            
            # Obtener NCF si existe
            ncf = picking.l10n_do_ncf_id.l10n_latam_document_number if picking.l10n_do_ncf_id else ''
            
            report_data.append({
                'ncf': ncf,
                'ncf_modified': '',
                'income_type': '01',  # Gastos (por defecto)
                'date': picking.date_done.date() if picking.date_done else picking.scheduled_date,
                'supplier_rnc': picking.partner_id.vat or '',
                'supplier_name': picking.partner_id.name,
                'billing_affected': '',
                'subtotal': subtotal,
                'itbis': itbis,
                'itbis_retained': 0.0,
                'itbis_perceived': 0.0,
                'isr_retained': 0.0,
                'selective_tax': 0.0,
                'other_taxes': 0.0,
                'legal_tip': 0.0,
                'total': total,
                'reference': picking.name,
            })
        
        return report_data
    
    def _get_607_data(self):
        """Obtener datos para reporte 607 (Ventas)"""
        StockPicking = self.env['stock.picking']
        
        # Buscar entregas (outgoing)
        domain = [
            ('picking_type_code', '=', 'outgoing'),
            ('state', '=', 'done'),
            ('date_done', '>=', fields.Datetime.combine(self.date_from, fields.Datetime.min.time())),
            ('date_done', '<=', fields.Datetime.combine(self.date_to, fields.Datetime.max.time())),
            ('company_id', '=', self.company_id.id),
        ]
        
        pickings = StockPicking.search(domain)
        
        report_data = []
        
        for picking in pickings:
            if not picking.partner_id:
                continue
            
            # Calcular totales
            subtotal = 0.0
            itbis = 0.0
            
            for move in picking.move_ids:
                move_subtotal = move.product_uom_qty * move.price_unit
                move_itbis = move.l10n_do_itbis_amount or 0.0
                
                subtotal += move_subtotal
                itbis += move_itbis
            
            total = subtotal + itbis
            
            # Obtener NCF si existe
            ncf = picking.l10n_do_ncf_id.l10n_latam_document_number if picking.l10n_do_ncf_id else ''
            
            report_data.append({
                'ncf': ncf,
                'ncf_modified': '',
                'date': picking.date_done.date() if picking.date_done else picking.scheduled_date,
                'customer_rnc': picking.partner_id.vat or '',
                'customer_name': picking.partner_id.name,
                'billing_affected': '',
                'subtotal': subtotal,
                'itbis': itbis,
                'itbis_retained': 0.0,
                'itbis_perceived': 0.0,
                'isr_retained': 0.0,
                'selective_tax': 0.0,
                'other_taxes': 0.0,
                'legal_tip': 0.0,
                'total': total,
                'reference': picking.name,
            })
        
        return report_data
    
    def _generate_excel(self, report_data):
        """Generar reporte en Excel formato DGII"""
        if not xlsxwriter:
            raise UserError(_('La librería xlsxwriter no está instalada. Por favor, instálela con: pip install xlsxwriter'))
        
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet(f'Reporte {self.report_type}')
        
        # Formatos
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
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
            'border': 1,
            'text_wrap': True
        })
        
        number_format = workbook.add_format({'num_format': '#,##0.00', 'border': 1})
        text_format = workbook.add_format({'border': 1})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy', 'border': 1})
        
        # Título
        title = f'REPORTE {self.report_type} - {self.company_id.name}'
        worksheet.merge_range('A1:N1', title, title_format)
        worksheet.merge_range('A2:N2', 
            f'Período: {self.date_from.strftime("%d/%m/%Y")} - {self.date_to.strftime("%d/%m/%Y")}', 
            text_format)
        
        # Cabeceras según tipo de reporte
        row = 3
        
        if self.report_type == '606':
            headers = ['NCF', 'NCF Modificado', 'Tipo Ingreso', 'Fecha', 'RNC Proveedor', 
                      'Razón Social', 'Factura Afecta', 'Subtotal', 'ITBIS Facturado', 
                      'ITBIS Retenido', 'ITBIS Percibido', 'ISR Retenido', 'Imp. Selectivo',
                      'Otros Impuestos', 'Propina Legal', 'Total']
        else:
            headers = ['NCF', 'NCF Modificado', 'Fecha', 'RNC Cliente', 'Razón Social',
                      'Factura Afecta', 'Subtotal', 'ITBIS Facturado', 'ITBIS Retenido',
                      'ITBIS Percibido', 'ISR Retenido', 'Imp. Selectivo', 'Otros Impuestos',
                      'Propina Legal', 'Total', 'Referencia']
        
        for col, header in enumerate(headers):
            worksheet.write(row, col, header, header_format)
        
        # Datos
        row += 1
        totals = {
            'subtotal': 0.0,
            'itbis': 0.0,
            'total': 0.0,
        }
        
        for item in report_data:
            col = 0
            worksheet.write(row, col, item['ncf'], text_format); col += 1
            worksheet.write(row, col, item.get('ncf_modified', ''), text_format); col += 1
            
            if self.report_type == '606':
                worksheet.write(row, col, item.get('income_type', ''), text_format); col += 1
            
            worksheet.write_datetime(row, col, item['date'], date_format); col += 1
            
            rnc_key = 'supplier_rnc' if self.report_type == '606' else 'customer_rnc'
            name_key = 'supplier_name' if self.report_type == '606' else 'customer_name'
            
            worksheet.write(row, col, item[rnc_key], text_format); col += 1
            worksheet.write(row, col, item[name_key], text_format); col += 1
            worksheet.write(row, col, item.get('billing_affected', ''), text_format); col += 1
            worksheet.write(row, col, item['subtotal'], number_format); col += 1
            worksheet.write(row, col, item['itbis'], number_format); col += 1
            worksheet.write(row, col, item.get('itbis_retained', 0.0), number_format); col += 1
            worksheet.write(row, col, item.get('itbis_perceived', 0.0), number_format); col += 1
            worksheet.write(row, col, item.get('isr_retained', 0.0), number_format); col += 1
            worksheet.write(row, col, item.get('selective_tax', 0.0), number_format); col += 1
            worksheet.write(row, col, item.get('other_taxes', 0.0), number_format); col += 1
            worksheet.write(row, col, item.get('legal_tip', 0.0), number_format); col += 1
            worksheet.write(row, col, item['total'], number_format); col += 1
            
            if self.report_type == '607':
                worksheet.write(row, col, item.get('reference', ''), text_format)
            
            # Acumular totales
            totals['subtotal'] += item['subtotal']
            totals['itbis'] += item['itbis']
            totals['total'] += item['total']
            
            row += 1
        
        # Total
        worksheet.write(row, 6, 'TOTALES:', header_format)
        worksheet.write(row, 7, totals['subtotal'], number_format)
        worksheet.write(row, 8, totals['itbis'], number_format)
        worksheet.write(row, 15 if self.report_type == '606' else 14, totals['total'], number_format)
        
        # Ajustar anchos
        worksheet.set_column('A:A', 19)
        worksheet.set_column('B:B', 19)
        worksheet.set_column('C:C', 12)
        worksheet.set_column('D:D', 12)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 35)
        worksheet.set_column('G:P', 14)
        
        workbook.close()
        output.seek(0)
        
        # Guardar en el wizard
        filename = f'Reporte_{self.report_type}_{self.date_from.strftime("%Y%m")}_{self.date_to.strftime("%Y%m")}.xlsx'
        self.write({
            'excel_file': base64.b64encode(output.read()),
            'excel_filename': filename,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'l10n.do.606.607.wizard',
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
            'url': f'/web/content?model=l10n.do.606.607.wizard&id={self.id}&field=excel_file&filename={self.excel_filename}&download=true',
            'target': 'self',
        }

