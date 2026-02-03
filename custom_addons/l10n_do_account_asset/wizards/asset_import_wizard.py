# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
from io import BytesIO


class AssetImportWizard(models.TransientModel):
    _name = 'asset.import.wizard'
    _description = 'Asistente de Importación de Activos'

    file = fields.Binary(
        string='Archivo Excel',
        required=True
    )
    filename = fields.Char(
        string='Nombre del Archivo'
    )
    default_category_id = fields.Many2one(
        'account.asset.category',
        string='Categoría por Defecto',
        help='Se usará si no se especifica categoría en el archivo'
    )

    def action_import(self):
        """Importa activos desde Excel"""
        self.ensure_one()
        
        try:
            import openpyxl
        except ImportError:
            raise UserError(_('La biblioteca openpyxl no está instalada.'))
        
        # Lee archivo Excel
        excel_data = base64.b64decode(self.file)
        workbook = openpyxl.load_workbook(BytesIO(excel_data))
        sheet = workbook.active
        
        # Procesa filas (asume primera fila son encabezados)
        created_count = 0
        errors = []
        
        for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            try:
                # Extrae datos (ajusta según formato de archivo)
                name = row[0]
                category_code = row[1] if len(row) > 1 else None
                purchase_value = float(row[2]) if len(row) > 2 and row[2] else 0.0
                acquisition_date = row[3] if len(row) > 3 else fields.Date.today()
                
                if not name:
                    continue
                
                # Busca categoría
                category = None
                if category_code:
                    category = self.env['account.asset.category'].search([
                        ('code', '=', category_code)
                    ], limit=1)
                if not category and self.default_category_id:
                    category = self.default_category_id
                
                if not category:
                    errors.append(f'Fila {row_idx}: No se encontró categoría.')
                    continue
                
                # Crea activo
                self.env['account.asset'].create({
                    'name': name,
                    'category_id': category.id,
                    'purchase_value': purchase_value,
                    'acquisition_date': acquisition_date,
                })
                created_count += 1
                
            except Exception as e:
                errors.append(f'Fila {row_idx}: {str(e)}')
        
        # Mensaje de resultado
        message = f'{created_count} activos importados.'
        if errors:
            message += '\n\nErrores:\n' + '\n'.join(errors)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Importación Completada'),
                'message': message,
                'sticky': True,
                'type': 'success' if not errors else 'warning',
            }
        }

