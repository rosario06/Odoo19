# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AssetComputeWizard(models.TransientModel):
    _name = 'asset.compute.wizard'
    _description = 'Asistente de Cálculo de Depreciación'

    date = fields.Date(
        string='Fecha de Depreciación',
        required=True,
        default=fields.Date.context_today
    )
    asset_ids = fields.Many2many(
        'account.asset',
        string='Activos',
        help='Dejar vacío para procesar todos los activos en uso'
    )
    
    def action_compute_depreciation(self):
        """Calcula y contabiliza la depreciación"""
        self.ensure_one()
        
        # Obtiene activos a procesar
        if self.asset_ids:
            assets = self.asset_ids
        else:
            assets = self.env['account.asset'].search([('state', '=', 'running')])
        
        if not assets:
            raise UserError(_('No hay activos para procesar.'))
        
        # Procesa cada activo
        processed = 0
        for asset in assets:
            lines = asset.depreciation_line_ids.filtered(
                lambda l: l.state == 'draft' and l.depreciation_date <= self.date
            )
            for line in lines:
                try:
                    line.action_post()
                    processed += 1
                except Exception as e:
                    continue
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Depreciación Calculada'),
                'message': _('%s líneas de depreciación contabilizadas.') % processed,
                'sticky': False,
                'type': 'success',
            }
        }

