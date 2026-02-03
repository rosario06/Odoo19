# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    # Configuración e-CF (ya definidos en l10n_do_ext, solo los referenciamos)
    # Si no existen en l10n_do_ext, se pueden descomentar:
    
    # l10n_do_ecf_enabled = fields.Boolean(
    #     string='Habilitar e-CF',
    #     help='Habilita la facturación electrónica DGII (e-CF)'
    # )
    
    # l10n_do_ecf_test_mode = fields.Boolean(
    #     string='Modo de Pruebas',
    #     help='Usar ambiente de pruebas de DGII (testecf)',
    #     default=True
    # )
    
    # l10n_do_ecf_service_url = fields.Char(
    #     string='URL Servicios DGII',
    #     default='https://ecf.dgii.gov.do/testecf/ws/recepcionecf'
    # )
    
    # l10n_do_ecf_certificate = fields.Binary(
    #     string='Certificado Digital',
    #     help='Certificado PKCS#12 (.p12 o .pfx)',
    #     attachment=True
    # )
    
    # l10n_do_ecf_certificate_password = fields.Char(
    #     string='Contraseña Certificado'
    # )
    
    # l10n_do_ecf_security_code = fields.Char(
    #     string='Código de Seguridad DGII'
    # )
    
    # Estadísticas e-CF
    ecf_sent_count = fields.Integer(
        string='e-CF Enviados',
        compute='_compute_ecf_stats'
    )
    
    ecf_approved_count = fields.Integer(
        string='e-CF Aprobados',
        compute='_compute_ecf_stats'
    )
    
    ecf_rejected_count = fields.Integer(
        string='e-CF Rechazados',
        compute='_compute_ecf_stats'
    )

    def _compute_ecf_stats(self):
        for company in self:
            ecf_docs = self.env['ecf.document'].search([
                ('company_id', '=', company.id)
            ])
            
            company.ecf_sent_count = len(ecf_docs.filtered(lambda d: d.state in ['sent', 'approved']))
            company.ecf_approved_count = len(ecf_docs.filtered(lambda d: d.state == 'approved'))
            company.ecf_rejected_count = len(ecf_docs.filtered(lambda d: d.state == 'rejected'))

    def action_view_ecf_documents(self):
        """Abre la lista de documentos e-CF de la compañía"""
        self.ensure_one()
        
        return {
            'name': _('Documentos e-CF'),
            'type': 'ir.actions.act_window',
            'res_model': 'ecf.document',
            'view_mode': 'tree,form',
            'domain': [('company_id', '=', self.id)],
            'context': {'default_company_id': self.id},
        }

