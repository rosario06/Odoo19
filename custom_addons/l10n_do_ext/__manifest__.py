# -*- coding: utf-8 -*-

{
    'name': 'República Dominicana - Contabilidad Extendida',
    'version': '19.0.1.0.0',
    'category': 'Localization/Account Charts',
    'summary': 'Localización Extendida: NCF, Reportes DGII, e-CF y más para República Dominicana',
    'description': """
Módulo de Localización Extendida para República Dominicana (l10n_do_ext)
=========================================================================

Este módulo extiende la funcionalidad de l10n_do con características avanzadas
para cumplir con las regulaciones fiscales de la DGII en Odoo 19.

Características principales:
----------------------------
* **Gestión de NCF (Número de Comprobante Fiscal):**
  - Secuencias automáticas para cada tipo de comprobante (01, 02, 03, 04, 07, 11, 12, 13, 14, 15).
  - Validación de formato y rangos.
  - Gestión avanzada con estados (activo, vencido, agotado).
* **Plan Contable:**
  - Plan de cuentas con estructura de 8 dígitos (compatible DGII y NIIF).
  - Más de 70 cuentas preconfiguradas.
  - Cuentas detalladas para efectivo, bancos, inventarios, activos fijos.
* **Impuestos y Retenciones:**
  - ITBIS 18%, 16%, 0% para ventas y compras.
  - Retenciones de ITBIS (100%, 75%).
  - Retenciones de ISR (2%, 5%, 10%, 27%).
  - Grupos especializados: Telecomunicaciones, Construcción, Servicios Profesionales.
* **Posiciones Fiscales:**
  - Automatización de impuestos según el tipo de operación.
  - Ventas al Estado (exención automática).
  - Compras al exterior (retención ISR 27%).
  - Personas físicas servicios (retención ISR 27%).
  - Materiales de construcción (ITBIS + Ret 75%).
* **Reportes Fiscales:**
  - Generación de reportes 606 (Compras) y 607 (Ventas).
  - Exportación a formato TXT oficial DGII.
* **Facturación Electrónica (e-CF):**
  - Configuración para certificados digitales.
  - Generación de códigos QR.
  - Integración con servicios DGII (base preparada).

Este módulo cumple con las normas y regulaciones de la DGII y es compatible con NIIF.
    """,
    'author': 'Juan Rosario / Consultorio developers',
    'website': 'https://www.linkedin.com/in/jrosariom/',
    'depends': [
        'account',
        'account_edi',
        'l10n_latam_base',
        'l10n_latam_invoice_document',  # Proporciona l10n_latam_document_number
        'l10n_do',  # Requiere el módulo base oficial de Odoo
    ],
    'data': [
        # Seguridad
        'security/ir.model.access.csv',
        # Datos base
        'data/l10n_do_chart_template.xml',
        # 'data/l10n_do_chart_template_extended.xml',  # Deshabilitado - Odoo 19 no usa templates
        # 'data/l10n_do_taxes.xml',  # Deshabilitado - Odoo 19 no usa tax templates
        # 'data/l10n_do_taxes_advanced.xml',  # Deshabilitado - Odoo 19 no usa tax templates
        # 'data/l10n_do_fiscal_positions.xml',  # Deshabilitado - Odoo 19 no usa fiscal position templates
        'data/l10n_do_ncf_sequences.xml',
        # Vistas
        'views/res_company_views.xml',
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
        'views/account_move_views.xml',
        'views/l10n_do_dgii_report_views.xml',
        # Wizards
        'wizard/l10n_do_dgii_report_wizard_views.xml',
        'wizard/l10n_do_config_wizard_views.xml',
    ],
    'external_dependencies': {
        'python': ['qrcode'],
    },
    # Demo data deshabilitado temporalmente por validaciones de formato VAT
    # 'demo': [
    #     'demo/demo_data.xml',
    # ],
    'installable': True,
    'auto_install': False, # Se instalará manualmente
    'application': True, # Aparece en el listado de Apps
    'license': 'LGPL-3',
    'sequence': 100,
    'images': ['static/description/banner.svg', 'static/description/icon.svg'],
}