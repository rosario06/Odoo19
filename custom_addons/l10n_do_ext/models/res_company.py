# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re


class ResCompany(models.Model):
    _inherit = 'res.company'

    # --- Campos para República Dominicana ---
    
    l10n_do_rnc = fields.Char(
        string='RNC',
        help='Registro Nacional del Contribuyente (RNC) de la empresa',
        size=11,
    )
    
    l10n_do_dgii_tax_payer_type = fields.Selection(
        [
            ('normal', 'Régimen Normal'),
            ('simplified', 'Régimen Simplificado'),
            ('special', 'Régimen Especial'),
            ('none', 'No Contribuyente'),
        ],
        string='Tipo de Contribuyente',
        default='normal',
        help='Tipo de contribuyente registrado en la DGII',
    )
    
    l10n_do_default_sale_fiscal_type = fields.Selection(
        [
            ('fiscal', 'Factura con Valor Fiscal'),
            ('final', 'Factura para Consumidor Final'),
            ('gov', 'Factura Gubernamental'),
            ('special', 'Factura Régimen Especial'),
            ('export', 'Factura de Exportación'),
        ],
        string='Tipo Fiscal de Venta por Defecto',
        default='fiscal',
        help='Tipo de comprobante fiscal por defecto para ventas',
    )
    
    l10n_do_ncf_expiration_date = fields.Date(
        string='Fecha de Vencimiento NCF',
        help='Fecha de vencimiento de la secuencia de NCF autorizada por la DGII',
    )
    
    l10n_do_purchase_journal_id = fields.Many2one(
        'account.journal',
        string='Diario de Compras',
        domain=[('type', '=', 'purchase')],
        help='Diario por defecto para facturas de compra con NCF',
    )
    
    # Campos para Facturación Electrónica (e-CF)
    l10n_do_ecf_enabled = fields.Boolean(
        string='Facturación Electrónica Habilitada',
        help='Habilita el sistema de Facturación Electrónica DGII (e-CF)',
    )
    
    l10n_do_ecf_test_mode = fields.Boolean(
        string='Modo de Pruebas e-CF',
        default=True,
        help='Usar ambiente de pruebas de DGII para e-CF',
    )
    
    l10n_do_ecf_service_url = fields.Char(
        string='URL Servicios DGII',
        compute='_compute_ecf_service_url',
        store=True,
        readonly=False,
        help='URL de los servicios web de DGII para e-CF',
    )
    
    l10n_do_ecf_certificate = fields.Binary(
        string='Certificado Digital (.p12)',
        help='Certificado digital PKCS#12 para firma electrónica',
    )
    
    l10n_do_ecf_certificate_password = fields.Char(
        string='Contraseña del Certificado',
        help='Contraseña del archivo de certificado digital',
    )
    
    l10n_do_ecf_security_code = fields.Char(
        string='Código de Seguridad',
        help='Código de seguridad proporcionado por la DGII',
    )

    @api.depends('l10n_do_ecf_test_mode')
    def _compute_ecf_service_url(self):
        """Calcula la URL del servicio según el modo (pruebas/producción)."""
        for company in self:
            if company.l10n_do_ecf_test_mode:
                company.l10n_do_ecf_service_url = 'https://ecf.dgii.gov.do/testecf'
            else:
                company.l10n_do_ecf_service_url = 'https://ecf.dgii.gov.do/ecf'

    @api.constrains('l10n_do_rnc')
    def _check_l10n_do_rnc(self):
        """Valida el formato del RNC."""
        for company in self:
            if company.country_id.code == 'DO' and company.l10n_do_rnc:
                # Validar que solo contenga dígitos
                if not company.l10n_do_rnc.isdigit():
                    raise ValidationError(_("El RNC debe contener solo números."))
                
                # Validar longitud (9 dígitos para RNC, 11 para cédula)
                if len(company.l10n_do_rnc) not in (9, 11):
                    raise ValidationError(_("El RNC debe tener 9 dígitos o 11 dígitos si es una cédula."))

    def _localization_use_documents(self):
        """Habilita el uso de documentos LATAM para República Dominicana."""
        self.ensure_one()
        if self.country_id.code == 'DO':
            return True
        return super()._localization_use_documents()

    def write(self, vals):
        """Validaciones adicionales al actualizar la compañía."""
        # Validar configuración de e-CF
        if any(field in vals for field in ['l10n_do_ecf_enabled', 'l10n_do_ecf_certificate', 'l10n_do_ecf_certificate_password']):
            for company in self:
                ecf_enabled = vals.get('l10n_do_ecf_enabled', company.l10n_do_ecf_enabled)
                ecf_certificate = vals.get('l10n_do_ecf_certificate', company.l10n_do_ecf_certificate)
                ecf_password = vals.get('l10n_do_ecf_certificate_password', company.l10n_do_ecf_certificate_password)
                
                if ecf_enabled and not (ecf_certificate and ecf_password):
                    raise ValidationError(_(
                        "Para habilitar la facturación electrónica debe configurar el certificado digital y su contraseña."
                    ))
        
        return super().write(vals)

