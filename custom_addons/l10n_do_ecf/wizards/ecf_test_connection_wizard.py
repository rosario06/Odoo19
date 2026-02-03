# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class EcfTestConnectionWizard(models.TransientModel):
    _name = 'ecf.test.connection.wizard'
    _description = 'Wizard de Prueba de Conexión DGII'

    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company
    )
    
    result_message = fields.Text(
        string='Resultado',
        readonly=True
    )
    
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('done', 'Completado'),
    ], default='draft')

    def action_test(self):
        """Prueba la conexión con DGII"""
        self.ensure_one()
        
        company = self.company_id
        
        if not company.l10n_do_ecf_enabled:
            raise UserError(_('La facturación electrónica no está habilitada para esta compañía.'))
        
        # Probar conexión
        result = self.env['ecf.webservice'].test_connection(company)
        
        if result['success']:
            self.result_message = _(
                '✓ CONEXIÓN EXITOSA\n\n'
                'URL: %s\n'
                'Modo: %s\n'
                'RNC: %s\n\n'
                'El servidor DGII está accesible y respondiendo correctamente.'
            ) % (
                result['url'],
                'Pruebas' if company.l10n_do_ecf_test_mode else 'Producción',
                company.vat or 'No configurado'
            )
        else:
            self.result_message = _(
                '✗ ERROR DE CONEXIÓN\n\n'
                'URL intentada: %s\n'
                'Error: %s\n\n'
                'Verifique:\n'
                '• Conexión a Internet\n'
                '• Firewall/Proxy\n'
                '• URL de servicios DGII\n'
                '• Certificado SSL'
            ) % (result['url'], result['message'])
        
        self.state = 'done'
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ecf.test.connection.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

