# -*- coding: utf-8 -*-
{
    'name': 'República Dominicana - Inventario',
    'version': '19.0.1.0.0',
    'category': 'Localization/Inventory',
    'summary': 'Localización de Inventario y Almacén para República Dominicana',
    'description': '''
República Dominicana - Inventario y Almacén
=============================================

Módulo de localización de inventario para República Dominicana que incluye:

**Conduce (Documento de Transporte):**
- Generación de conduces según normativa DGII
- Numeración automática secuencial
- Campos obligatorios: chofer, vehículo, placa, origen/destino
- Impresión en formato oficial
- Validaciones de completitud
- Estados: borrador, validado, cancelado

**Reportes DGII:**
- Reporte 606 (Compras) para movimientos de inventario
- Reporte 607 (Ventas) para salidas de inventario
- Reporte de existencias valoradas
- Exportación a Excel formato DGII
- Filtros por período y almacén

**Kardex Detallado:**
- Kardex por producto (PEPS, UEPS, Promedio)
- Movimientos de entrada/salida
- Saldos en cantidad y valor
- Costos unitarios
- Exportación a Excel

**Extensiones de Productos:**
- Código arancelario (ITBIS)
- Clasificación fiscal DGII
- Exonerado/Gravado
- Tipo de producto para reportes

**Valorización Fiscal:**
- Métodos de valorización según normativa RD
- Costo promedio ponderado
- PEPS (Primero en Entrar, Primero en Salir)
- Reportes de valorización

**Integración con NCF:**
- Vinculación de movimientos con NCF
- Conduce asociado a factura
- Validaciones fiscales en transferencias

**Trazabilidad:**
- Números de lote/serie con formato RD
- Seguimiento completo de movimientos
- Auditoría de cambios

**Características:**
- Multi-almacén
- Multi-compañía
- Integración contable completa
- Validaciones fiscales automáticas
- Reportes personalizables
    ''',
    'author': 'Juan Rosario',
    'website': 'https://github.com/juanrosario/l10n_do_stock',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'stock',                # Inventario base
        'stock_account',        # Contabilidad de inventario
        'l10n_do',              # Plan contable RD
        'l10n_do_ext',          # Extensiones de localización RD
    ],
    'data': [
        # Seguridad
        'security/l10n_do_stock_security.xml',
        'security/ir.model.access.csv',
        
        # Datos maestros
        'data/l10n_do_conduce_sequence.xml',
        # 'data/product_category_data.xml',
        
        # Vistas
        'views/product_template_views.xml',
        'views/stock_picking_views.xml',
        'views/l10n_do_conduce_views.xml',
        
        # Wizards (CARGAR ANTES DE LOS MENÚS)
        'wizards/l10n_do_conduce_wizard_views.xml',
        'wizards/l10n_do_inventory_report_wizard_views.xml',
        'wizards/l10n_do_kardex_wizard_views.xml',
        'wizards/l10n_do_606_607_wizard_views.xml',
        
        # Menús (CARGAR DESPUÉS DE TODO)
        'views/menus.xml',
        
        # Reportes PDF
        'reports/conduce_report.xml',
        'reports/inventory_report_template.xml',
        'reports/kardex_report_template.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}

