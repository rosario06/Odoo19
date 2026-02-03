# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MinimumWage(models.Model):
    _name = 'minimum.wage'
    _description = 'Salario Mínimo'
    _order = 'date_from desc, id desc'
    
    name = fields.Char(
        string='Descripción',
        required=True,
        help="Descripción del salario mínimo (ej: 'Salario Mínimo 2025')"
    )
    
    date_from = fields.Date(
        string='Válido Desde',
        required=True,
        default=fields.Date.today,
        help="Fecha desde la cual aplica este salario mínimo"
    )
    
    date_to = fields.Date(
        string='Válido Hasta',
        help="Fecha hasta la cual aplica este salario mínimo. Dejar vacío si es indefinido"
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
    
    # Salarios mínimos por sector/categoría
    # Sector Privado
    private_sector_large = fields.Float(
        string='Sector Privado - Grandes Empresas (DOP/mes)',
        required=True,
        digits=(16, 2),
        default=21000.00,
        help="Salario mínimo para empresas grandes del sector privado (más de 50 empleados)"
    )
    
    private_sector_medium = fields.Float(
        string='Sector Privado - Medianas Empresas (DOP/mes)',
        required=True,
        digits=(16, 2),
        default=18000.00,
        help="Salario mínimo para empresas medianas del sector privado (11-50 empleados)"
    )
    
    private_sector_small = fields.Float(
        string='Sector Privado - Pequeñas Empresas (DOP/mes)',
        required=True,
        digits=(16, 2),
        default=16000.00,
        help="Salario mínimo para pequeñas empresas del sector privado (hasta 10 empleados)"
    )
    
    # Sector Público
    public_sector = fields.Float(
        string='Sector Público (DOP/mes)',
        required=True,
        digits=(16, 2),
        default=21000.00,
        help="Salario mínimo para el sector público"
    )
    
    # Zonas Francas
    free_zone = fields.Float(
        string='Zonas Francas (DOP/mes)',
        required=True,
        digits=(16, 2),
        default=17500.00,
        help="Salario mínimo para empresas de zonas francas"
    )
    
    # Sector Agropecuario
    agricultural = fields.Float(
        string='Sector Agropecuario (DOP/mes)',
        required=True,
        digits=(16, 2),
        default=14000.00,
        help="Salario mínimo para el sector agropecuario"
    )
    
    # Construcción
    construction = fields.Float(
        string='Construcción (DOP/mes)',
        required=True,
        digits=(16, 2),
        default=18000.00,
        help="Salario mínimo para el sector construcción"
    )
    
    # Turismo y Hoteles
    tourism_hotels = fields.Float(
        string='Turismo y Hoteles (DOP/mes)',
        required=True,
        digits=(16, 2),
        default=19000.00,
        help="Salario mínimo para sector turismo y hoteles"
    )
    
    # Campo adicional para clasificación personalizada
    category = fields.Selection([
        ('general', 'General'),
        ('private', 'Sector Privado'),
        ('public', 'Sector Público'),
        ('zone_franca', 'Zona Franca'),
        ('agriculture', 'Agropecuario'),
        ('construction', 'Construcción'),
        ('tourism', 'Turismo'),
        ('other', 'Otro')
    ], string='Categoría', default='general', required=True)
    
    notes = fields.Text(
        string='Notas',
        help="Notas adicionales sobre este salario mínimo"
    )
    
    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if record.date_to and record.date_from > record.date_to:
                raise ValidationError(_("La fecha 'Válido Desde' debe ser menor que 'Válido Hasta'"))
    
    @api.constrains('private_sector_large', 'private_sector_medium', 'private_sector_small',
                    'public_sector', 'free_zone', 'agricultural', 'construction', 'tourism_hotels')
    def _check_amounts(self):
        for record in self:
            amounts = [
                record.private_sector_large, record.private_sector_medium, record.private_sector_small,
                record.public_sector, record.free_zone, record.agricultural,
                record.construction, record.tourism_hotels
            ]
            if any(amount <= 0 for amount in amounts):
                raise ValidationError(_("Los salarios mínimos deben ser mayores a cero"))
    
    @api.model
    def get_minimum_wage_for_date(self, date=None, company_id=None, sector='private_sector_large'):
        """
        Obtiene el salario mínimo vigente para una fecha y sector determinado
        
        :param date: Fecha para la cual se busca el salario mínimo. Si es None, usa la fecha actual
        :param company_id: ID de la compañía. Si es None, usa la compañía actual
        :param sector: Sector para el cual se busca el salario ('private_sector_large', 'public_sector', etc.)
        :return: Float con el salario mínimo o 0.0 si no se encuentra
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
        
        record = self.search(domain, order='date_from desc', limit=1)
        
        if record and hasattr(record, sector):
            return getattr(record, sector, 0.0)
        return 0.0
    
    @api.model
    def get_record_for_date(self, date=None, company_id=None):
        """
        Obtiene el registro completo de salario mínimo vigente para una fecha
        
        :param date: Fecha para la cual se busca el salario mínimo
        :param company_id: ID de la compañía
        :return: Recordset de minimum.wage o False
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
    
    def name_get(self):
        result = []
        for record in self:
            if record.date_to:
                name = f"{record.name} ({record.date_from} - {record.date_to})"
            else:
                name = f"{record.name} (Desde {record.date_from})"
            result.append((record.id, name))
        return result

