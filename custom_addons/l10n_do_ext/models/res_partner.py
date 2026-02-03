# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # --- Campos para República Dominicana ---
    
    l10n_do_dgii_tax_payer_type = fields.Selection(
        [
            ('taxpayer', 'Contribuyente'),
            ('non_taxpayer', 'No Contribuyente'),
            ('special', 'Régimen Especial'),
            ('governmental', 'Gubernamental'),
            ('foreigner', 'Extranjero'),
        ],
        string='Tipo de Contribuyente DGII',
        default='taxpayer',
        help='Tipo de contribuyente según la DGII',
    )
    
    l10n_do_identification_type = fields.Selection(
        [
            ('rnc', 'RNC (Registro Nacional del Contribuyente)'),
            ('ced', 'Cédula de Identidad'),
            ('passport', 'Pasaporte'),
        ],
        string='Tipo de Identificación',
        help='Tipo de documento de identificación fiscal',
    )
    
    l10n_do_sale_fiscal_type = fields.Selection(
        [
            ('01', 'Factura de Crédito Fiscal'),
            ('02', 'Factura de Consumo'),
            ('14', 'Factura Régimen Especial'),
            ('15', 'Factura Gubernamental'),
        ],
        string='Tipo Fiscal para Ventas',
        help='Tipo de comprobante fiscal a usar por defecto en ventas a este cliente',
    )
    
    l10n_do_expense_type = fields.Selection(
        [
            ('01', 'Gastos de Personal'),
            ('02', 'Gastos por Trabajos, Suministros y Servicios'),
            ('03', 'Arrendamientos'),
            ('04', 'Gastos de Activos Fijos'),
            ('05', 'Gastos de Representación'),
            ('06', 'Otras Deducciones Admitidas'),
            ('07', 'Gastos Financieros'),
            ('08', 'Gastos Extraordinarios'),
            ('09', 'Compras y Gastos que forman parte del Costo de Venta'),
            ('10', 'Adquisiciones de Activos'),
            ('11', 'Gastos de Seguros'),
        ],
        string='Tipo de Gasto',
        help='Clasificación del tipo de gasto para reportes a la DGII (606)',
    )
    
    l10n_do_apply_itbis_withholding = fields.Boolean(
        string='Aplica Retención de ITBIS',
        default=False,
        help='Indica si este proveedor está sujeto a retención de ITBIS',
    )
    
    l10n_do_apply_isr_withholding = fields.Boolean(
        string='Aplica Retención ISR',
        default=False,
        help='Indica si este proveedor está sujeto a retención de ISR',
    )
    
    l10n_do_isr_withholding_percent = fields.Float(
        string='% Retención ISR',
        default=10.0,
        help='Porcentaje de retención de ISR aplicable',
    )

    @api.constrains('vat', 'country_id', 'l10n_do_identification_type')
    def _check_l10n_do_vat(self):
        """Valida el formato del RNC o Cédula para República Dominicana."""
        for partner in self:
            if partner.country_id.code == 'DO' and partner.vat:
                # Eliminar espacios, guiones y prefijo de país
                vat = partner.vat.replace('-', '').replace(' ', '').upper()
                if vat.startswith('DO'):
                    vat = vat[2:]
                
                # Validar que solo contenga dígitos
                if not vat.isdigit():
                    raise ValidationError(_("El RNC o Cédula debe contener solo números."))
                
                # Determinar tipo de identificación automáticamente
                if len(vat) == 9:
                    if not partner.l10n_do_identification_type:
                        partner.l10n_do_identification_type = 'rnc'
                    elif partner.l10n_do_identification_type != 'rnc':
                        raise ValidationError(_("Un RNC debe tener exactamente 9 dígitos."))
                
                elif len(vat) == 11:
                    if not partner.l10n_do_identification_type:
                        partner.l10n_do_identification_type = 'ced'
                    elif partner.l10n_do_identification_type != 'ced':
                        raise ValidationError(_("Una Cédula debe tener exactamente 11 dígitos."))
                
                else:
                    raise ValidationError(_("El RNC debe tener 9 dígitos y la Cédula 11 dígitos. Recibido: %s dígitos") % len(vat))

    @api.onchange('l10n_do_dgii_tax_payer_type')
    def _onchange_l10n_do_dgii_tax_payer_type(self):
        """Configura valores por defecto según el tipo de contribuyente."""
        if self.l10n_do_dgii_tax_payer_type == 'non_taxpayer':
            self.l10n_do_sale_fiscal_type = '02'  # Factura de Consumo
            self.l10n_do_apply_itbis_withholding = False
            self.l10n_do_apply_isr_withholding = False
        elif self.l10n_do_dgii_tax_payer_type == 'governmental':
            self.l10n_do_sale_fiscal_type = '15'  # Factura Gubernamental
        elif self.l10n_do_dgii_tax_payer_type == 'special':
            self.l10n_do_sale_fiscal_type = '14'  # Factura Régimen Especial
        else:
            self.l10n_do_sale_fiscal_type = '01'  # Factura de Crédito Fiscal

    def _display_address(self, without_company=False):
        """Personaliza el formato de dirección para República Dominicana."""
        if self.country_id.code == 'DO':
            address_format = '%(street)s\n%(city)s, %(state_code)s %(zip)s\n%(country_name)s'
            if self.vat:
                address_format = 'RNC/Cédula: %(vat)s\n' + address_format
            return address_format
        return super()._display_address(without_company=without_company)

