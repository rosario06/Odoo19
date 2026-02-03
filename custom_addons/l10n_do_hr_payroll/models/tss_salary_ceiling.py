# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TSSSalaryCeiling(models.Model):
    _name = 'tss.salary.ceiling'
    _description = 'Tope Salarial TSS'
    _order = 'date_from desc, id desc'
    
    name = fields.Char(
        string='Descripción',
        required=True,
        help="Descripción del tope (ej: 'Tope Salarial TSS 2025')"
    )
    
    date_from = fields.Date(
        string='Válido Desde',
        required=True,
        default=fields.Date.today,
        help="Fecha desde la cual aplica este tope"
    )
    
    date_to = fields.Date(
        string='Válido Hasta',
        help="Fecha hasta la cual aplica este tope. Dejar vacío si es indefinido"
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
    
    # Topes salariales
    afp_ceiling = fields.Float(
        string='Tope AFP (DOP)',
        required=True,
        digits=(16, 2),
        default=0.0,
        help="Salario máximo cotizable para AFP. 0 = sin límite"
    )
    
    ars_ceiling = fields.Float(
        string='Tope ARS (DOP)',
        required=True,
        digits=(16, 2),
        default=0.0,
        help="Salario máximo cotizable para ARS. 0 = sin límite"
    )
    
    sfs_ceiling = fields.Float(
        string='Tope SFS (DOP)',
        required=True,
        digits=(16, 2),
        default=0.0,
        help="Salario máximo cotizable para SFS. 0 = sin límite"
    )
    
    # Salarios mínimos cotizables
    afp_min_salary = fields.Float(
        string='Salario Mínimo AFP (DOP)',
        digits=(16, 2),
        default=0.0,
        help="Salario mínimo cotizable para AFP"
    )
    
    ars_min_salary = fields.Float(
        string='Salario Mínimo ARS (DOP)',
        digits=(16, 2),
        default=0.0,
        help="Salario mínimo cotizable para ARS"
    )
    
    sfs_min_salary = fields.Float(
        string='Salario Mínimo SFS (DOP)',
        digits=(16, 2),
        default=0.0,
        help="Salario mínimo cotizable para SFS"
    )
    
    notes = fields.Text(
        string='Notas',
        help="Notas adicionales sobre este tope"
    )
    
    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if record.date_to and record.date_from > record.date_to:
                raise ValidationError(_("La fecha 'Válido Desde' debe ser menor que 'Válido Hasta'"))
    
    @api.constrains('afp_ceiling', 'ars_ceiling', 'sfs_ceiling',
                    'afp_min_salary', 'ars_min_salary', 'sfs_min_salary')
    def _check_amounts(self):
        for record in self:
            amounts = [
                record.afp_ceiling, record.ars_ceiling, record.sfs_ceiling,
                record.afp_min_salary, record.ars_min_salary, record.sfs_min_salary
            ]
            if any(amount < 0 for amount in amounts):
                raise ValidationError(_("Los montos no pueden ser negativos"))
    
    @api.model
    def get_ceiling_for_date(self, date=None, company_id=None):
        """
        Obtiene los topes salariales vigentes para una fecha determinada
        
        :param date: Fecha para la cual se buscan los topes. Si es None, usa la fecha actual
        :param company_id: ID de la compañía. Si es None, usa la compañía actual
        :return: Recordset de tss.salary.ceiling o False si no se encuentra
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
        
        return self.search(domain, order='date_from desc', limit=1)
    
    def apply_ceiling(self, amount, ceiling_type='afp'):
        """
        Aplica el tope salarial correspondiente a un monto
        
        :param amount: Monto al cual aplicar el tope
        :param ceiling_type: Tipo de tope ('afp', 'ars', 'sfs')
        :return: Monto con tope aplicado
        """
        self.ensure_one()
        ceiling_field = f'{ceiling_type}_ceiling'
        ceiling = getattr(self, ceiling_field, 0.0)
        
        if ceiling > 0:
            return min(amount, ceiling)
        return amount
    
    def name_get(self):
        result = []
        for record in self:
            if record.date_to:
                name = f"{record.name} ({record.date_from} - {record.date_to})"
            else:
                name = f"{record.name} (Desde {record.date_from})"
            result.append((record.id, name))
        return result

