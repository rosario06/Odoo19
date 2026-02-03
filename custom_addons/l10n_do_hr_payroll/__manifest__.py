# -*- coding: utf-8 -*-
{
    'name': 'República Dominicana - Nómina',
    'version': '19.0.1.0.0',
    'category': 'Localization',
    'summary': 'Localización de Nómina para República Dominicana',
    'description': '''
República Dominicana - Nómina
===============================

Módulo de localización de nómina para República Dominicana que incluye:

**Seguridad Social (TSS):**
- AFP (Administradora de Fondos de Pensiones)
- ARS (Administradora de Riesgos de Salud)
- SFS (Seguro Familiar de Salud)
- Cálculo automático de aportes patronales y laborales
- Tasas configurables por período

**Impuesto Sobre la Renta (ISR):**
- Cálculo escalonado según tabla de la DGII
- Deducción de dependientes
- Otros gastos deducibles
- Tabla de tramos configurables

**Prestaciones Laborales:**
- Cesantía
- Vacaciones
- Salario de Navidad (Bono Navideño)
- Preaviso
- Aprovisionamiento mensual

**Otras Deducciones:**
- Coop

erativa
- Préstamos
- Anticipos
- Inasistencias

**Reportes:**
- Nómina detallada
- TSS (Planilla TSS)
- ISR (Reporte 607)
- Prestaciones laborales
- DGT's (Formularios del Ministerio de Trabajo)

**Características:**
- Tasas dinámicas configurables
- Histórico de cambios de tasas
- Salario mínimo configurable
- Multi-compañía
- Integración contable completa
    ''',
    'author': 'Juan Rosario',
    'website': 'https://github.com/juanrosario/l10n_do_hr_payroll',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'hr',                   # Empleados
        'hr_payroll',           # OCA Payroll (Community)
        'hr_payroll_account',   # OCA Payroll Accounting
        'l10n_do',              # Plan contable RD
        'l10n_do_ext',          # Extensiones de localización RD
    ],
    'data': [
        # Seguridad
        'security/hr_payroll_do_security.xml',
        'security/ir.model.access.csv',
        
        # Datos maestros
        'data/hr_salary_rule_category_data.xml',
        'data/hr_contribution_register_data.xml',
        'data/tss_rate_config_data.xml',
        'data/isr_tax_bracket_data.xml',
        'data/minimum_wage_data.xml',
        'data/hr_salary_rule_data.xml',
        'data/hr_payroll_structure_data.xml',
        
        # Vistas
        'views/tss_rate_config_views.xml',
        'views/isr_tax_bracket_views.xml',
        'views/minimum_wage_views.xml',
        'views/tss_salary_ceiling_views.xml',
        'views/tss_contribution_views.xml',
        'views/isr_payroll_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_payslip_views.xml',
        'views/hr_employee_views.xml',
        'views/provision_laborales_views.xml',
        'views/menus.xml',
        
        # Wizards (COMENTADO TEMPORALMENTE - agregar en actualización futura)
        # 'wizards/hr_payroll_tss_report_views.xml',
        # 'wizards/hr_payroll_isr_report_views.xml',
        
        # Reportes (COMENTADO TEMPORALMENTE - agregar en actualización futura)
        # 'reports/payslip_report_templates.xml',
        # 'reports/tss_report_templates.xml',
        # 'reports/isr_report_templates.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}

