# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
from io import BytesIO
try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None


class L10nDoKardexWizard(models.TransientModel):
    _name = 'l10n.do.kardex.wizard'
    _description = 'Asistente de Generación de Kardex'
    
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
    
    product_ids = fields.Many2many(
        'product.product',
        string='Productos',
        help="Dejar vacío para incluir todos los productos"
    )
    
    location_ids = fields.Many2many(
        'stock.location',
        string='Ubicaciones',
        domain="[('usage', '=', 'internal')]",
        help="Dejar vacío para incluir todas las ubicaciones"
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company
    )
    
    report_format = fields.Selection([
        ('pdf', 'PDF'),
        ('excel', 'Excel')
    ], string='Formato', default='excel', required=True)
    
    valuation_method = fields.Selection([
        ('fifo', 'PEPS (Primero en Entrar, Primero en Salir)'),
        ('average', 'Costo Promedio Ponderado')
    ], string='Método de Valorización', default='average', required=True)
    
    show_zero_qty = fields.Boolean(
        string='Mostrar Productos sin Movimientos',
        default=False
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
    
    def action_generate_kardex(self):
        """Generar el kardex"""
        self.ensure_one()
        
        if self.date_from > self.date_to:
            raise UserError(_('La fecha inicial no puede ser mayor que la fecha final.'))
        
        # Obtener movimientos
        kardex_data = self._get_kardex_data()
        
        if not kardex_data and not self.show_zero_qty:
            raise UserError(_('No se encontraron movimientos de inventario para los filtros seleccionados.'))
        
        if self.report_format == 'excel':
            return self._generate_excel(kardex_data)
        else:
            return self._generate_pdf(kardex_data)
    
    def _get_kardex_data(self):
        """Obtener datos del kardex"""
        StockMove = self.env['stock.move']
        
        # Construir dominio
        domain = [
            ('date', '>=', fields.Datetime.combine(self.date_from, fields.Datetime.min.time())),
            ('date', '<=', fields.Datetime.combine(self.date_to, fields.Datetime.max.time())),
            ('state', '=', 'done'),
            ('company_id', '=', self.company_id.id),
        ]
        
        if self.product_ids:
            domain.append(('product_id', 'in', self.product_ids.ids))
        
        if self.location_ids:
            domain.append('|')
            domain.append(('location_id', 'in', self.location_ids.ids))
            domain.append(('location_dest_id', 'in', self.location_ids.ids))
        
        moves = StockMove.search(domain, order='date asc, id asc')
        
        # Agrupar por producto
        kardex_by_product = {}
        
        for move in moves:
            product = move.product_id
            if product.id not in kardex_by_product:
                kardex_by_product[product.id] = {
                    'product': product,
                    'moves': [],
                    'balance_qty': 0.0,
                    'balance_value': 0.0,
                }
            
            # Determinar si es entrada o salida
            is_in = False
            is_out = False
            
            if self.location_ids:
                if move.location_dest_id.id in self.location_ids.ids:
                    is_in = True
                if move.location_id.id in self.location_ids.ids:
                    is_out = True
            else:
                if move.location_dest_id.usage == 'internal':
                    is_in = True
                if move.location_id.usage == 'internal':
                    is_out = True
            
            qty_in = move.product_uom_qty if is_in else 0.0
            qty_out = move.product_uom_qty if is_out else 0.0
            
            # Calcular valores
            unit_cost = move.price_unit or product.standard_price
            value_in = qty_in * unit_cost
            value_out = qty_out * unit_cost
            
            # Actualizar saldo
            kardex_by_product[product.id]['balance_qty'] += (qty_in - qty_out)
            kardex_by_product[product.id]['balance_value'] += (value_in - value_out)
            
            kardex_by_product[product.id]['moves'].append({
                'date': move.date,
                'reference': move.reference or move.picking_id.name or move.name,
                'partner': move.picking_id.partner_id.name if move.picking_id and move.picking_id.partner_id else '',
                'qty_in': qty_in,
                'qty_out': qty_out,
                'qty_balance': kardex_by_product[product.id]['balance_qty'],
                'unit_cost': unit_cost,
                'value_in': value_in,
                'value_out': value_out,
                'value_balance': kardex_by_product[product.id]['balance_value'],
            })
        
        return kardex_by_product
    
    def _generate_excel(self, kardex_data):
        """Generar reporte en Excel"""
        if not xlsxwriter:
            raise UserError(_('La librería xlsxwriter no está instalada. Por favor, instálela con: pip install xlsxwriter'))
        
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        
        # Formatos
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#002D62',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        subtitle_format = workbook.add_format({
            'bold': True,
            'bg_color': '#ED1C24',
            'font_color': 'white',
            'align': 'left',
            'valign': 'vcenter',
            'border': 1
        })
        
        number_format = workbook.add_format({'num_format': '#,##0.00', 'border': 1})
        text_format = workbook.add_format({'border': 1})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy', 'border': 1})
        
        # Crear hoja para cada producto
        for product_id, data in kardex_data.items():
            product = data['product']
            sheet_name = product.default_code or str(product.id)
            sheet_name = sheet_name[:31]  # Excel limita a 31 caracteres
            
            worksheet = workbook.add_worksheet(sheet_name)
            
            # Título
            worksheet.merge_range('A1:L1', f'KARDEX - {product.name}', title_format)
            worksheet.merge_range('A2:L2', f'Período: {self.date_from.strftime("%d/%m/%Y")} - {self.date_to.strftime("%d/%m/%Y")}', text_format)
            
            # Cabeceras
            row = 3
            headers = ['Fecha', 'Referencia', 'Cliente/Proveedor', 'Entrada', 'Salida', 'Saldo Qty',
                      'Costo Unit.', 'Valor Entrada', 'Valor Salida', 'Saldo Valor']
            for col, header in enumerate(headers):
                worksheet.write(row, col, header, header_format)
            
            # Datos
            row += 1
            for move_data in data['moves']:
                worksheet.write_datetime(row, 0, move_data['date'], date_format)
                worksheet.write(row, 1, move_data['reference'], text_format)
                worksheet.write(row, 2, move_data['partner'], text_format)
                worksheet.write(row, 3, move_data['qty_in'], number_format)
                worksheet.write(row, 4, move_data['qty_out'], number_format)
                worksheet.write(row, 5, move_data['qty_balance'], number_format)
                worksheet.write(row, 6, move_data['unit_cost'], number_format)
                worksheet.write(row, 7, move_data['value_in'], number_format)
                worksheet.write(row, 8, move_data['value_out'], number_format)
                worksheet.write(row, 9, move_data['value_balance'], number_format)
                row += 1
            
            # Ajustar anchos
            worksheet.set_column('A:A', 12)
            worksheet.set_column('B:B', 20)
            worksheet.set_column('C:C', 25)
            worksheet.set_column('D:J', 12)
        
        workbook.close()
        output.seek(0)
        
        # Guardar en el wizard
        filename = f'Kardex_{self.date_from}_{self.date_to}.xlsx'
        self.write({
            'excel_file': base64.b64encode(output.read()),
            'excel_filename': filename,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'l10n.do.kardex.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'show_download': True},
        }
    
    def _generate_pdf(self, kardex_data):
        """Generar reporte en PDF"""
        # TODO: Implementar generación de PDF con QWeb
        raise UserError(_('La generación de PDF estará disponible próximamente. Use formato Excel.'))
    
    def action_download_excel(self):
        """Descargar el archivo Excel"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content?model=l10n.do.kardex.wizard&id={self.id}&field=excel_file&filename={self.excel_filename}&download=true',
            'target': 'self',
        }

