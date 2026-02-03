# -*- coding: utf-8 -*-
{
    'name': 'República Dominicana - Facturación Electrónica DGII (e-CF)',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Integración completa de Facturación Electrónica DGII para República Dominicana',
    'description': '''
        Facturación Electrónica DGII (e-CF) para República Dominicana
        ============================================================
        
        Funcionalidades:
        ----------------
        * Generación de Comprobantes Fiscales Electrónicos (e-CF)
        * Firma digital de documentos con certificado PKCS#12
        * Envío automático a servicios DGII (testecf/producción)
        * Recepción de Acuse de Recibo
        * Aprobación Comercial
        * Anulación de e-NCF
        * Representación impresa con código QR
        * Validación de esquemas XSD según DGII v1.0
        * Consulta de estado de e-CF
        * Manejo de errores y reintentos automáticos
        * Cola de envío asíncrono
        * Certificación DGII (testecf → producción)
        
        Requisitos:
        -----------
        * Certificado digital .p12/.pfx de entidad certificadora autorizada
        * Registro en portal DGII
        * Autorización DGII para emisión electrónica
        * RNC activo
        
        Dependencias Python:
        -------------------
        * zeep (SOAP webservices)
        * xmlsec (firma digital XML)
        * cryptography (manejo certificados)
        * qrcode (códigos QR)
        * lxml (procesamiento XML)
    ''',
    'author': 'Juan Rosario / Consultorio developers',
    'website': 'https://www.linkedin.com/in/jrosariom/',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'l10n_do',
        'l10n_do_ext',
        'l10n_latam_invoice_document',
    ],
    'external_dependencies': {
        'python': [
            'zeep',
            # 'xmlsec',  # Opcional - Comentado temporalmente por incompatibilidad en Windows
            'cryptography',
            'qrcode',
            'lxml',
            'requests',
        ],
    },
    'data': [
        # Security (primero los grupos)
        'security/ecf_security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/ecf_sequences.xml',
        'data/ecf_document_types.xml',
        
        # Views
        'views/ecf_document_views.xml',
        'views/ecf_certificate_views.xml',
        'views/account_move_views.xml',
        'views/res_company_views.xml',
        'views/res_config_settings_views.xml',
        'views/ecf_menus.xml',
        
        # Wizards
        'wizards/ecf_send_wizard_views.xml',
        'wizards/ecf_test_connection_wizard_views.xml',
        
        # Reports
        'reports/ecf_report_templates.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 101,
    'images': [
        'static/description/banner.svg',
        'static/description/icon.svg',
    ],
}

