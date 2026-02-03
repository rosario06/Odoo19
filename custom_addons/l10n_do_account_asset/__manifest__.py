# -*- coding: utf-8 -*-
{
    'name': 'República Dominicana - Activos Fijos',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Gestión de Activos Fijos con Depreciación según Normativa DGII',
    'description': """
República Dominicana - Activos Fijos
=====================================

Gestión completa de activos fijos con depreciación automática según tasas DGII.

Características principales:
* Registro completo de activos fijos
* Categorías predefinidas según DGII con tasas oficiales
* Depreciación automática (lineal y acelerada)
* Integración con contabilidad (asientos automáticos)
* Mantenimientos y garantías
* Baja y venta de activos
* Reportes fiscales formato DGII
* Cálculo automático desde facturas con NCF
* Dashboard de activos
* Cron job para depreciación mensual

Tasas de Depreciación DGII:
* Edificios: 5% anual
* Vehículos: 25% anual
* Maquinaria: 15% anual
* Equipos de oficina: 20% anual
* Computadoras: 33.33% anual
* Herramientas: 25% anual

Normativa Legal:
* Ley 11-92 (Código Tributario RD)
* Norma 02-05 (Reglamento ISR)
* Norma General 06-2018 (NCF)
* NIC 16 (Propiedad, Planta y Equipo)
    """,
    'author': 'Juan Rosario',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'l10n_do',
        'l10n_latam_invoice_document',
        'product',
    ],
    'external_dependencies': {
        'python': ['xlsxwriter'],
    },
    'assets': {
        'web.assets_backend': [
            'l10n_do_account_asset/static/webclient/src/css/asset_form_fix.css',
        ],
    },
    'data': [
        # Seguridad (PRIMERO)
        'security/asset_security.xml',
        'security/ir.model.access.csv',
        
        # Datos maestros
        'data/asset_sequence.xml',
        'data/asset_category_data.xml',
        'data/depreciation_cron.xml',
        
        # Vistas
        'views/account_asset_category_views.xml',
        'views/account_asset_views.xml',
        'views/account_asset_depreciation_views.xml',
        'views/account_asset_maintenance_views.xml',
        'views/account_move_views.xml',
        
        # Wizards (ANTES DE LOS MENÚS)
        'wizards/asset_compute_wizard_views.xml',
        'wizards/asset_disposal_wizard_views.xml',
        'wizards/asset_report_wizard_views.xml',
        'wizards/asset_import_wizard_views.xml',
        
        # Menús (DESPUÉS DE TODO)
        'views/menus.xml',
        
        # Reportes PDF
        'reports/asset_report.xml',
        'reports/depreciation_report.xml',
        'reports/dgii_report_template.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}

