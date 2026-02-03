# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta


class AccountAsset(models.Model):
    _name = 'account.asset'
    _description = 'Activo Fijo'
    _inherit = ['mail.thread']
    _order = 'acquisition_date desc, name'

    # Información básica
    name = fields.Char(
        string='Nombre del Activo',
        required=True,
        tracking=True,
        index=True
    )
    code = fields.Char(
        string='Código',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Nuevo'),
        tracking=True,
        index=True
    )
    category_id = fields.Many2one(
        'account.asset.category',
        string='Categoría',
        required=True,
        tracking=True
    )
    state = fields.Selection(
        [
            ('draft', 'Borrador'),
            ('running', 'En Uso'),
            ('close', 'Cerrado'),
            ('disposed', 'Dado de Baja'),
        ],
        string='Estado',
        default='draft',
        required=True,
        tracking=True
    )
    
    # Información de adquisición
    acquisition_date = fields.Date(
        string='Fecha de Adquisición',
        required=True,
        default=fields.Date.context_today,
        tracking=True
    )
    first_depreciation_date = fields.Date(
        string='Fecha Primera Depreciación',
        help='Fecha desde la cual comienza la depreciación'
    )
    purchase_value = fields.Monetary(
        string='Valor de Compra',
        required=True,
        currency_field='currency_id',
        tracking=True
    )
    salvage_value = fields.Monetary(
        string='Valor Residual',
        currency_field='currency_id',
        help='Valor estimado al final de la vida útil',
        tracking=True
    )
    
    # Factura de compra
    invoice_id = fields.Many2one(
        'account.move',
        string='Factura de Compra',
        domain="[('move_type', '=', 'in_invoice')]",
        tracking=True
    )
    l10n_do_ncf = fields.Char(
        string='NCF',
        related='invoice_id.l10n_latam_document_number',
        store=True,
        help='Número de Comprobante Fiscal'
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Proveedor',
        related='invoice_id.partner_id',
        store=True
    )
    
    # Depreciación
    depreciation_rate = fields.Float(
        string='Tasa de Depreciación (%)',
        related='category_id.depreciation_rate',
        readonly=True
    )
    depreciation_method = fields.Selection(
        related='category_id.depreciation_method',
        readonly=True
    )
    depreciation_line_ids = fields.One2many(
        'account.asset.depreciation',
        'asset_id',
        string='Líneas de Depreciación'
    )
    depreciation_value = fields.Monetary(
        string='Valor Depreciable',
        compute='_compute_depreciation_value',
        store=True,
        currency_field='currency_id'
    )
    depreciated_value = fields.Monetary(
        string='Depreciación Acumulada',
        compute='_compute_depreciation_values',
        currency_field='currency_id',
        store=True
    )
    book_value = fields.Monetary(
        string='Valor en Libros',
        compute='_compute_depreciation_values',
        currency_field='currency_id',
        store=True
    )
    
    # Ubicación y responsable
    location = fields.Char(
        string='Ubicación Física',
        tracking=True
    )
    responsible_id = fields.Many2one(
        'res.users',
        string='Responsable',
        tracking=True
    )
    
    # Información adicional
    serial_number = fields.Char(
        string='Número de Serie',
        tracking=True
    )
    manufacturer = fields.Char(
        string='Fabricante'
    )
    model = fields.Char(
        string='Modelo'
    )
    warranty_start_date = fields.Date(
        string='Inicio de Garantía'
    )
    warranty_end_date = fields.Date(
        string='Fin de Garantía'
    )
    warranty_active = fields.Boolean(
        string='Garantía Activa',
        compute='_compute_warranty_active'
    )
    
    # Mantenimientos
    maintenance_ids = fields.One2many(
        'account.asset.maintenance',
        'asset_id',
        string='Mantenimientos'
    )
    maintenance_count = fields.Integer(
        string='Mantenimientos',
        compute='_compute_maintenance_count'
    )
    next_maintenance_date = fields.Date(
        string='Próximo Mantenimiento'
    )
    
    # Información contable
    account_asset_id = fields.Many2one(
        'account.account',
        string='Cuenta de Activo',
        related='category_id.account_asset_id',
        readonly=True
    )
    account_depreciation_id = fields.Many2one(
        'account.account',
        string='Cuenta de Depreciación',
        related='category_id.account_depreciation_id',
        readonly=True
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Diario',
        related='category_id.journal_id',
        readonly=True
    )
    move_ids = fields.One2many(
        'account.move',
        'asset_id',
        string='Asientos Contables'
    )
    
    # Imágenes y documentos
    image = fields.Binary(
        string='Imagen',
        attachment=True
    )
    attachment_count = fields.Integer(
        string='Documentos',
        compute='_compute_attachment_count'
    )
    
    # Otros
    active = fields.Boolean(
        default=True
    )
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        default=lambda self: self.env.company,
        required=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        related='company_id.currency_id',
        readonly=True
    )
    note = fields.Html(
        string='Notas'
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Sobrescribe create para asignar secuencia"""
        for vals in vals_list:
            if vals.get('code', _('Nuevo')) == _('Nuevo'):
                vals['code'] = self.env['ir.sequence'].next_by_code('account.asset') or _('Nuevo')
        return super().create(vals_list)

    @api.depends('purchase_value', 'salvage_value')
    def _compute_depreciation_value(self):
        """Calcula el valor depreciable"""
        for asset in self:
            asset.depreciation_value = asset.purchase_value - asset.salvage_value

    @api.depends('depreciation_line_ids.amount', 'depreciation_line_ids.state')
    def _compute_depreciation_values(self):
        """Calcula valores de depreciación"""
        for asset in self:
            posted_lines = asset.depreciation_line_ids.filtered(lambda l: l.state == 'posted')
            asset.depreciated_value = sum(posted_lines.mapped('amount'))
            asset.book_value = asset.purchase_value - asset.depreciated_value

    @api.depends('warranty_end_date')
    def _compute_warranty_active(self):
        """Verifica si la garantía está activa"""
        today = fields.Date.context_today(self)
        for asset in self:
            asset.warranty_active = bool(
                asset.warranty_end_date and asset.warranty_end_date >= today
            )

    def _compute_maintenance_count(self):
        """Cuenta los mantenimientos"""
        for asset in self:
            asset.maintenance_count = len(asset.maintenance_ids)

    def _compute_attachment_count(self):
        """Cuenta los documentos adjuntos"""
        for asset in self:
            asset.attachment_count = self.env['ir.attachment'].search_count([
                ('res_model', '=', 'account.asset'),
                ('res_id', '=', asset.id)
            ])

    @api.constrains('purchase_value', 'salvage_value')
    def _check_values(self):
        """Valida que los valores sean correctos"""
        for asset in self:
            if asset.purchase_value < 0:
                raise ValidationError(_('El valor de compra no puede ser negativo.'))
            if asset.salvage_value < 0:
                raise ValidationError(_('El valor residual no puede ser negativo.'))
            if asset.salvage_value >= asset.purchase_value:
                raise ValidationError(_('El valor residual debe ser menor al valor de compra.'))

    def action_draft(self):
        """Vuelve el activo a borrador"""
        self.write({'state': 'draft'})

    def action_running(self):
        """Activa el activo y genera líneas de depreciación"""
        for asset in self:
            if not asset.first_depreciation_date:
                asset.first_depreciation_date = asset.acquisition_date
            
            # Genera líneas de depreciación
            asset._generate_depreciation_lines()
            asset.write({'state': 'running'})

    def action_close(self):
        """Cierra el activo"""
        self.write({'state': 'close'})

    def _generate_depreciation_lines(self):
        """Genera las líneas de depreciación automáticas"""
        self.ensure_one()
        
        # Elimina líneas existentes en borrador
        self.depreciation_line_ids.filtered(lambda l: l.state == 'draft').unlink()
        
        if self.depreciation_value <= 0:
            return
        
        # Calcula número de meses
        months = int(self.category_id.useful_life_years * 12)
        monthly_depreciation = self.depreciation_value / months
        
        depreciation_date = self.first_depreciation_date
        
        for i in range(months):
            # Ajusta último mes para cuadrar
            if i == months - 1:
                remaining = self.depreciation_value - (monthly_depreciation * (months - 1))
                monthly_depreciation = remaining
            
            self.env['account.asset.depreciation'].create({
                'asset_id': self.id,
                'name': f'{self.name} - {depreciation_date.strftime("%m/%Y")}',
                'depreciation_date': depreciation_date,
                'amount': monthly_depreciation,
                'state': 'draft',
            })
            
            depreciation_date = depreciation_date + relativedelta(months=1)

    def action_view_maintenances(self):
        """Acción para ver mantenimientos"""
        self.ensure_one()
        return {
            'name': _('Mantenimientos'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.asset.maintenance',
            'view_mode': 'list,form',
            'domain': [('asset_id', '=', self.id)],
            'context': {'default_asset_id': self.id},
        }

    def action_view_depreciation_lines(self):
        """Acción para ver líneas de depreciación"""
        self.ensure_one()
        return {
            'name': _('Depreciación'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.asset.depreciation',
            'view_mode': 'list,form',
            'domain': [('asset_id', '=', self.id)],
            'context': {'default_asset_id': self.id},
        }

    def action_view_attachments(self):
        """Acción para ver documentos adjuntos"""
        self.ensure_one()
        return {
            'name': _('Documentos'),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'list,form',
            'domain': [('res_model', '=', 'account.asset'), ('res_id', '=', self.id)],
            'context': {
                'default_res_model': 'account.asset',
                'default_res_id': self.id,
            },
        }

