# -*- coding: utf-8 -*-

from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    # Información fiscal RD
    rnc = fields.Char(
        string='RNC',
        help="Registro Nacional de Contribuyentes"
    )
    
    cedula = fields.Char(
        string='Cédula',
        help="Cédula de Identidad y Electoral"
    )
    
    passport = fields.Char(
        string='Pasaporte',
        help="Número de pasaporte (para extranjeros)"
    )
    
    # Información TSS
    tss_number = fields.Char(
        string='Número TSS',
        help="Número de afiliación a la Tesorería de la Seguridad Social"
    )
    
    # Información bancaria
    bank_account_id = fields.Many2one(
        'res.partner.bank',
        string='Cuenta Bancaria',
        help="Cuenta bancaria para depósito de nómina"
    )

