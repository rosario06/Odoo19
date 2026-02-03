# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrContract(models.Model):
    _inherit = 'hr.contract'
    
    # Información TSS
    afp_number = fields.Char(
        string='Número AFP',
        help="Número de afiliación a la AFP del empleado"
    )
    
    ars_number = fields.Char(
        string='Número ARS',
        help="Número de afiliación a la ARS del empleado"
    )
    
    ars_provider = fields.Char(
        string='ARS Proveedor',
        help="Nombre de la ARS del empleado"
    )
    
    sfs_type = fields.Selection([
        ('state', 'Plan Estatal (SENASA)'),
        ('private', 'Plan Privado (ARS)')
    ], string='Tipo SFS', default='state',
        help="Tipo de plan de salud del empleado"
    )
    
    # Configuración de salario
    minimum_wage_sector = fields.Selection([
        ('private_sector_large', 'Sector Privado - Grandes Empresas'),
        ('private_sector_medium', 'Sector Privado - Medianas Empresas'),
        ('private_sector_small', 'Sector Privado - Pequeñas Empresas'),
        ('public_sector', 'Sector Público'),
        ('free_zone', 'Zonas Francas'),
        ('agricultural', 'Sector Agropecuario'),
        ('construction', 'Construcción'),
        ('tourism_hotels', 'Turismo y Hoteles')
    ], string='Sector Salario Mínimo', default='private_sector_large',
        help="Sector para determinación del salario mínimo")
    
    # ISR - Deducciones personales
    isr_dependents = fields.Integer(
        string='Dependientes para ISR',
        default=0,
        help="Número de dependientes para deducción de ISR"
    )
    
    isr_other_deductions = fields.Float(
        string='Otras Deducciones ISR (DOP/mes)',
        digits=(16, 2),
        default=0.0,
        help="Otras deducciones mensuales permitidas por ley (educación, seguros, etc.)"
    )
    
    # Otras deducciones
    cooperative_amount = fields.Float(
        string='Cooperativa (DOP/mes)',
        digits=(16, 2),
        default=0.0,
        help="Monto mensual de aporte a cooperativa"
    )
    
    loan_amount = fields.Float(
        string='Préstamo (DOP/mes)',
        digits=(16, 2),
        default=0.0,
        help="Monto mensual de deducción por préstamo"
    )
    
    # Prestaciones laborales
    provision_enabled = fields.Boolean(
        string='Calcular Provisiones',
        default=True,
        help="Si está activo, se calcularán las provisiones de cesantía, preaviso y vacaciones"
    )
    
    vacation_days_per_year = fields.Integer(
        string='Días de Vacaciones/Año',
        default=14,
        help="Días de vacaciones por año trabajado según legislación dominicana"
    )
    
    @api.onchange('minimum_wage_sector')
    def _onchange_minimum_wage_sector(self):
        """Advertir si el salario es menor al mínimo del sector"""
        if self.wage and self.minimum_wage_sector:
            MinWage = self.env['minimum.wage']
            min_wage = MinWage.get_minimum_wage_for_date(
                date=self.date_start or fields.Date.today(),
                sector=self.minimum_wage_sector
            )
            if min_wage > 0 and self.wage < min_wage:
                return {
                    'warning': {
                        'title': 'Salario Inferior al Mínimo',
                        'message': f'El salario ({self.wage:,.2f}) es inferior al salario mínimo del sector ({min_wage:,.2f})'
                    }
                }

