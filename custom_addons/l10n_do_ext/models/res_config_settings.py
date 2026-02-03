# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # NOTA: La configuración de e-CF se realiza desde Ajustes → Empresas → Mi Empresa
    # No se incluye aquí debido a limitaciones de evaluación de expresiones en Odoo 19

