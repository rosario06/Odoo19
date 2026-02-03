# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ISRTaxBracket(models.Model):
    _name = 'isr.tax.bracket'
    _description = 'Tramo de Impuesto Sobre la Renta (ISR)'
    _order = 'date_from desc, sequence, amount_from'
    
    name = fields.Char(
        string='Nombre',
        required=True,
        help="Nombre del tramo (ej: 'Tramo 1 - Exento')"
    )
    
    sequence = fields.Integer(
        string='Secuencia',
        default=10,
        help="Orden de aplicación del tramo"
    )
    
    date_from = fields.Date(
        string='Válido Desde',
        required=True,
        default=fields.Date.today,
        help="Fecha desde la cual aplica este tramo"
    )
    
    date_to = fields.Date(
        string='Válido Hasta',
        help="Fecha hasta la cual aplica este tramo. Dejar vacío si es indefinido"
    )
    
    active = fields.Boolean(
        string='Activo',
        default=True
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        default=lambda self: self.env.company,
        required=True
    )
    
    # Rangos del tramo
    amount_from = fields.Float(
        string='Desde (DOP/año)',
        required=True,
        digits=(16, 2),
        help="Monto mínimo del tramo (anual)"
    )
    
    amount_to = fields.Float(
        string='Hasta (DOP/año)',
        digits=(16, 2),
        help="Monto máximo del tramo (anual). 0 = sin límite"
    )
    
    # Tasa y excedente
    tax_rate = fields.Float(
        string='Tasa (%)',
        required=True,
        digits=(5, 2),
        help="Porcentaje de impuesto aplicable al excedente"
    )
    
    fixed_amount = fields.Float(
        string='Monto Fijo (DOP)',
        digits=(16, 2),
        default=0.0,
        help="Impuesto fijo acumulado de tramos anteriores"
    )
    
    # Información adicional
    exempt_amount = fields.Float(
        string='Monto Exento (DOP/año)',
        compute='_compute_exempt_amount',
        store=True,
        digits=(16, 2),
        help="Monto exento anual (primer tramo con tasa 0%)"
    )
    
    description = fields.Text(
        string='Descripción',
        help="Descripción detallada del tramo"
    )
    
    @api.depends('amount_from', 'tax_rate')
    def _compute_exempt_amount(self):
        for record in self:
            # El monto exento es el amount_to del primer tramo (tasa 0%)
            if record.tax_rate == 0:
                record.exempt_amount = record.amount_to or record.amount_from
            else:
                record.exempt_amount = 0.0
    
    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if record.date_to and record.date_from > record.date_to:
                raise ValidationError(_("La fecha 'Válido Desde' debe ser menor que 'Válido Hasta'"))
    
    @api.constrains('amount_from', 'amount_to')
    def _check_amounts(self):
        for record in self:
            if record.amount_from < 0:
                raise ValidationError(_("El monto 'Desde' no puede ser negativo"))
            if record.amount_to > 0 and record.amount_from >= record.amount_to:
                raise ValidationError(_("El monto 'Desde' debe ser menor que el monto 'Hasta'"))
    
    @api.constrains('tax_rate')
    def _check_tax_rate(self):
        for record in self:
            if record.tax_rate < 0 or record.tax_rate > 100:
                raise ValidationError(_("La tasa debe estar entre 0 y 100"))
    
    @api.model
    def get_brackets_for_date(self, date=None, company_id=None):
        """
        Obtiene todos los tramos de ISR vigentes para una fecha determinada
        
        :param date: Fecha para la cual se buscan los tramos. Si es None, usa la fecha actual
        :param company_id: ID de la compañía. Si es None, usa la compañía actual
        :return: Recordset de isr.tax.bracket ordenado por sequence, amount_from
        """
        if not date:
            date = fields.Date.today()
        if not company_id:
            company_id = self.env.company.id
        
        domain = [
            ('company_id', '=', company_id),
            ('date_from', '<=', date),
            ('active', '=', True),
            '|',
            ('date_to', '>=', date),
            ('date_to', '=', False)
        ]
        
        return self.search(domain, order='sequence, amount_from')
    
    @api.model
    def calculate_isr(self, annual_salary, date=None, company_id=None):
        """
        Calcula el ISR anual para un salario dado
        
        :param annual_salary: Salario anual gravable
        :param date: Fecha para determinar qué tramos usar
        :param company_id: ID de la compañía
        :return: Dict con el cálculo detallado del ISR
        """
        brackets = self.get_brackets_for_date(date, company_id)
        
        if not brackets:
            return {
                'annual_salary': annual_salary,
                'taxable_salary': annual_salary,
                'total_isr': 0.0,
                'effective_rate': 0.0,
                'brackets_applied': []
            }
        
        total_isr = 0.0
        brackets_applied = []
        remaining_salary = annual_salary
        
        for bracket in brackets:
            if remaining_salary <= 0:
                break
            
            # Determinar el monto aplicable en este tramo
            bracket_min = bracket.amount_from
            bracket_max = bracket.amount_to if bracket.amount_to > 0 else float('inf')
            
            if annual_salary > bracket_min:
                if annual_salary <= bracket_max:
                    # El salario cae dentro de este tramo
                    taxable_in_bracket = annual_salary - bracket_min
                else:
                    # El salario excede este tramo
                    taxable_in_bracket = bracket_max - bracket_min
                
                # Calcular ISR para este tramo
                isr_in_bracket = (taxable_in_bracket * bracket.tax_rate / 100) + bracket.fixed_amount
                total_isr = isr_in_bracket
                
                brackets_applied.append({
                    'bracket_name': bracket.name,
                    'from': bracket_min,
                    'to': bracket_max if bracket_max != float('inf') else 0,
                    'taxable_amount': taxable_in_bracket,
                    'rate': bracket.tax_rate,
                    'fixed_amount': bracket.fixed_amount,
                    'isr': isr_in_bracket
                })
                
                remaining_salary -= taxable_in_bracket
        
        effective_rate = (total_isr / annual_salary * 100) if annual_salary > 0 else 0.0
        
        return {
            'annual_salary': annual_salary,
            'taxable_salary': annual_salary,
            'total_isr': total_isr,
            'monthly_isr': total_isr / 12,
            'effective_rate': effective_rate,
            'brackets_applied': brackets_applied
        }
    
    def name_get(self):
        result = []
        for record in self:
            amount_to_str = f'{record.amount_to:,.2f}' if record.amount_to > 0 else 'en adelante'
            name = f"{record.name}: {record.amount_from:,.2f} - {amount_to_str} @ {record.tax_rate}%"
            result.append((record.id, name))
        return result

