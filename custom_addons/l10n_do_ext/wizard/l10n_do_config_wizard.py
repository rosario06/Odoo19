# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class L10nDoConfigWizard(models.TransientModel):
    _name = 'l10n.do.config.wizard'
    _description = 'Wizard de Configuración Inicial l10n_do'

    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company,
    )

    rnc_lookup_id = fields.Many2one(
        'l10n_do_ext.rnc.lookup',
        string='Buscar Empresa (Autocompletado)',
        help='Busque por nombre para encontrar los datos de la empresa automáticamente.',
    )
    
    # Paso 1: Información de la Empresa
    rnc = fields.Char(
        string='RNC de la Empresa',
        size=11,
        required=True,
        help='Registro Nacional del Contribuyente (9 dígitos)',
    )

    company_name = fields.Char(
        string='Nombre Encontrado',
        help='Nombre de la empresa encontrado en la DGII',
    )
    
    tax_payer_type = fields.Selection(
        [
            ('normal', 'Régimen Normal'),
            ('simplified', 'Régimen Simplificado'),
            ('special', 'Régimen Especial'),
        ],
        string='Tipo de Contribuyente',
        default='normal',
        required=True,
    )
    
    # Paso 2: Configuración de NCF
    ncf_expiration_date = fields.Date(
        string='Fecha de Vencimiento NCF',
        help='Fecha límite autorizada por la DGII para usar los NCF actuales',
    )
    
    configure_ncf_sequences = fields.Boolean(
        string='Configurar Secuencias NCF',
        default=True,
        help='Permite configurar los rangos de NCF autorizados por la DGII',
    )
    
    ncf_01_from = fields.Char(
        string='NCF 01 Desde',
        help='Ejemplo: B0100000001',
    )
    
    ncf_01_to = fields.Char(
        string='NCF 01 Hasta',
        help='Ejemplo: B0100001000',
    )
    
    ncf_02_from = fields.Char(
        string='NCF 02 Desde',
        help='Ejemplo: B0200000001',
    )
    
    ncf_02_to = fields.Char(
        string='NCF 02 Hasta',
        help='Ejemplo: B0200001000',
    )
    
    # Paso 3: Diarios
    configure_journals = fields.Boolean(
        string='Configurar Diarios Automáticamente',
        default=True,
    )
    
    sale_journal_id = fields.Many2one(
        'account.journal',
        string='Diario de Ventas',
        domain=[('type', '=', 'sale')],
    )
    
    purchase_journal_id = fields.Many2one(
        'account.journal',
        string='Diario de Compras',
        domain=[('type', '=', 'purchase')],
    )

    @api.constrains('rnc')
    def _check_rnc(self):
        """Valida el formato del RNC."""
        for wizard in self:
            if wizard.rnc:
                rnc = wizard.rnc.replace('-', '').replace(' ', '')
                if not rnc.isdigit():
                    raise ValidationError(_("El RNC debe contener solo números."))
                if len(rnc) not in (9, 11):
                    raise ValidationError(_("El RNC debe tener 9 dígitos (o 11 si es una cédula)."))

    def action_lookup_rnc(self):
        """Busca el nombre de la empresa en la DGII."""
        self.ensure_one()
        if not self.rnc:
            raise UserError(_("Por favor, ingrese un RNC primero."))
        
        rnc = self.rnc.replace('-', '').replace(' ', '')
        
        # En una demo, intentamos usar un servicio de consulta
        # Nota: La DGII oficial requiere manejo de sesiones. 
        # Aquí usamos una lógica de consulta simplificada.
        try:
            import requests
            import json
            
            # Intentar usar un servicio de consulta pública
            # Para la demo, simulamos la respuesta si el servicio oficial falla
            # o si no tenemos una API Key de un servicio pagado
            
            # Servicio público común para RNC (ejemplo didáctico)
            url = f"https://api.marcos.do/rnc/{rnc}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('name'):
                    self.company_name = data.get('name')
                    # Prellenar tipo de contribuyente si el servicio lo da
                    if data.get('taxpayer_type'):
                        self.tax_payer_type = 'normal' # Mapear si es posible
                    return {
                        'type': 'ir.actions.act_window',
                        'res_model': 'l10n.do.config.wizard',
                        'res_id': self.id,
                        'view_mode': 'form',
                        'target': 'new',
                    }
            
            # Fallback a búsqueda interna o mensaje si falla
            # (En producción se usaría un scraper más robusto)
            self.company_name = False
            raise UserError(_("No se pudo obtener el nombre automáticamente. Por favor ingréselo manualmente."))
            
        except Exception as e:
            self.company_name = False
            raise UserError(_("Error de conexión con DGII. Por favor ingrese el nombre manualmente."))
            
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'l10n.do.config.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_configure(self):
        """Aplica la configuración."""
        self.ensure_one()
        
        # Paso 1: Configurar la empresa
        vals = {
            'l10n_do_rnc': self.rnc.replace('-', '').replace(' ', ''),
            'l10n_do_dgii_tax_payer_type': self.tax_payer_type,
            'l10n_do_ncf_expiration_date': self.ncf_expiration_date,
            'l10n_do_purchase_journal_id': self.purchase_journal_id.id if self.purchase_journal_id else False,
        }
        if self.company_name:
            vals['name'] = self.company_name
            
        self.company_id.write(vals)
        
        # Paso 2: Configurar secuencias NCF (si se proporcionaron rangos)
        if self.configure_ncf_sequences:
            if self.ncf_01_from and self.ncf_01_to:
                self._configure_sequence('01', self.ncf_01_from, self.ncf_01_to)
            if self.ncf_02_from and self.ncf_02_to:
                self._configure_sequence('02', self.ncf_02_from, self.ncf_02_to)
        
        # Paso 3: Configurar diarios
        if self.configure_journals and self.sale_journal_id:
            # Obtener el tipo de documento NCF 01 (Factura de Crédito Fiscal)
            doc_type_01 = self.env['l10n_latam.document.type'].search([
                ('code', '=', '01'),
                ('country_id.code', '=', 'DO'),
            ], limit=1)
            
            if doc_type_01:
                self.sale_journal_id.write({
                    'l10n_latam_use_documents': True,
                    'l10n_latam_document_type_id': doc_type_01.id,
                })
        
        if self.configure_journals and self.purchase_journal_id:
            # Obtener el tipo de documento NCF 11 (Comprobante de Compras)
            doc_type_11 = self.env['l10n_latam.document.type'].search([
                ('code', '=', '11'),
                ('country_id.code', '=', 'DO'),
            ], limit=1)
            
            if doc_type_11:
                self.purchase_journal_id.write({
                    'l10n_latam_use_documents': True,
                    'l10n_latam_document_type_id': doc_type_11.id,
                })
        
        # Mensaje de éxito
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Configuración Completa'),
                'message': _('El módulo de localización dominicana ha sido configurado exitosamente.'),
                'type': 'success',
                'sticky': True,
                'next': {
                    'type': 'ir.actions.act_window_close',
                },
            }
        }

    def _configure_sequence(self, ncf_code, ncf_from, ncf_to):
        """Configura una secuencia NCF con los rangos proporcionados."""
        # Extraer el número inicial del NCF
        # Ejemplo: B0100000001 -> 1
        try:
            prefix = ncf_from[:3]  # B01
            number_from = int(ncf_from[3:])  # 00000001
            number_to = int(ncf_to[3:])
            
            # Buscar la secuencia
            sequence = self.env['ir.sequence'].search([
                ('code', '=', f'l10n_do.ncf.{ncf_code}'),
                '|',
                ('company_id', '=', self.company_id.id),
                ('company_id', '=', False),
            ], limit=1)
            
            if sequence:
                sequence.write({
                    'prefix': prefix,
                    'number_next': number_from,
                    'company_id': self.company_id.id,
                })
        except (ValueError, IndexError):
            raise ValidationError(_("El formato del NCF %s no es válido. Use el formato: B0100000001") % ncf_code)

    @api.onchange('rnc_lookup_id')
    def _onchange_rnc_lookup_id(self):
        """Prellenar datos desde el resultado de búsqueda externa."""
        if self.rnc_lookup_id:
            # Asegurar que traemos el dato, limpiando guiones o espacios
            if self.rnc_lookup_id.vat:
                rnc_limpio = self.rnc_lookup_id.vat.replace('-', '').replace(' ', '')
                self.rnc = rnc_limpio
            else:
                self.rnc = ''
                
            if self.rnc_lookup_id.name:
                self.company_name = self.rnc_lookup_id.name

    @api.onchange('company_id')
    def _onchange_company_id(self):
        """Prellenar datos de la empresa si existen."""
        if self.company_id:
            self.rnc = self.company_id.l10n_do_rnc or ''
            self.company_name = self.company_id.name or ''
            self.tax_payer_type = self.company_id.l10n_do_dgii_tax_payer_type or 'normal'
            self.ncf_expiration_date = self.company_id.l10n_do_ncf_expiration_date
            self.purchase_journal_id = self.company_id.l10n_do_purchase_journal_id
            
            # Buscar diarios por defecto
            if not self.sale_journal_id:
                self.sale_journal_id = self.env['account.journal'].search([
                    ('type', '=', 'sale'),
                    ('company_id', '=', self.company_id.id),
                ], limit=1)
            
            if not self.purchase_journal_id:
                self.purchase_journal_id = self.env['account.journal'].search([
                    ('type', '=', 'purchase'),
                    ('company_id', '=', self.company_id.id),
                ], limit=1)

