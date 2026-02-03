# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Nota: Los campos relacionados de e-CF ya están en res.company
    # Aquí solo creamos métodos de acción
    
    def action_test_ecf_connection(self):
        """Prueba la conexión con servicios DGII"""
        self.ensure_one()
        
        company = self.company_id
        
        if not company.l10n_do_ecf_enabled:
            raise UserError(_('La facturación electrónica no está habilitada.'))
        
        # Probar conexión usando el servicio
        result = self.env['ecf.webservice'].test_connection(company)
        
        if result['success']:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Conexión Exitosa'),
                    'message': _('La conexión con DGII se estableció correctamente.\nURL: %s') % result['url'],
                    'type': 'success',
                    'sticky': True,
                }
            }
        else:
            raise UserError(_('Error de conexión: %s') % result['message'])
    
    def action_view_ecf_certificates(self):
        """Abre la vista de certificados digitales"""
        return {
            'name': _('Certificados Digitales'),
            'type': 'ir.actions.act_window',
            'res_model': 'ecf.certificate',
            'view_mode': 'tree,form',
            'domain': [('company_id', '=', self.company_id.id)],
            'context': {'default_company_id': self.company_id.id},
        }

