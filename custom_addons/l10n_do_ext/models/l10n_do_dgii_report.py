# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import base64
import io


class L10nDoDgiiReport(models.Model):
    _name = 'l10n.do.dgii.report'
    _description = 'Reporte DGII (606/607)'
    _order = 'date_from desc'

    name = fields.Char(
        string='Nombre del Reporte',
        required=True,
        readonly=False,  # Removido states, manejado por la vista
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        readonly=True,
        default=lambda self: self.env.company,
    )
    
    report_type = fields.Selection(
        [
            ('606', 'Reporte 606 - Compras'),
            ('607', 'Reporte 607 - Ventas'),
        ],
        string='Tipo de Reporte',
        required=True,
        readonly=False,  # Removido states, manejado por la vista
    )
    
    date_from = fields.Date(
        string='Fecha Desde',
        required=True,
        readonly=False,  # Removido states, manejado por la vista
    )
    
    date_to = fields.Date(
        string='Fecha Hasta',
        required=True,
        readonly=False,  # Removido states, manejado por la vista
    )
    
    state = fields.Selection(
        [
            ('draft', 'Borrador'),
            ('generated', 'Generado'),
            ('sent', 'Enviado'),
            ('cancelled', 'Cancelado'),
        ],
        string='Estado',
        default='draft',
        readonly=True,
    )
    
    line_ids = fields.One2many(
        'l10n.do.dgii.report.line',
        'report_id',
        string='Líneas del Reporte',
        readonly=True,
    )
    
    total_amount = fields.Monetary(
        string='Monto Total',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    
    total_itbis = fields.Monetary(
        string='ITBIS Total',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    
    total_withholding = fields.Monetary(
        string='Retención Total',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    
    line_count = fields.Integer(
        string='Cantidad de Líneas',
        compute='_compute_totals',
        store=True,
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        related='company_id.currency_id',
        readonly=True,
    )
    
    txt_file = fields.Binary(
        string='Archivo TXT',
        readonly=True,
    )
    
    txt_filename = fields.Char(
        string='Nombre del Archivo TXT',
        readonly=True,
    )
    
    excel_file = fields.Binary(
        string='Archivo Excel',
        readonly=True,
    )
    
    excel_filename = fields.Char(
        string='Nombre del Archivo Excel',
        readonly=True,
    )

    @api.depends('line_ids.amount_total', 'line_ids.itbis_amount', 'line_ids.withholding_amount')
    def _compute_totals(self):
        """Calcula los totales del reporte."""
        for report in self:
            report.total_amount = sum(report.line_ids.mapped('amount_total'))
            report.total_itbis = sum(report.line_ids.mapped('itbis_amount'))
            report.total_withholding = sum(report.line_ids.mapped('withholding_amount'))
            report.line_count = len(report.line_ids)

    def action_generate_report(self):
        """Genera el reporte basado en las facturas del período."""
        self.ensure_one()
        
        if self.state != 'draft':
            raise UserError(_("Solo se pueden generar reportes en estado Borrador."))
        
        # Limpiar líneas existentes
        self.line_ids.unlink()
        
        # Buscar facturas según el tipo de reporte
        if self.report_type == '606':
            # Reporte de Compras (facturas de proveedor)
            invoices = self.env['account.move'].search([
                ('company_id', '=', self.company_id.id),
                ('move_type', 'in', ['in_invoice', 'in_refund']),
                ('state', '=', 'posted'),
                ('invoice_date', '>=', self.date_from),
                ('invoice_date', '<=', self.date_to),
                ('country_code', '=', 'DO'),
            ])
        else:
            # Reporte de Ventas (facturas de cliente)
            invoices = self.env['account.move'].search([
                ('company_id', '=', self.company_id.id),
                ('move_type', 'in', ['out_invoice', 'out_refund']),
                ('state', '=', 'posted'),
                ('invoice_date', '>=', self.date_from),
                ('invoice_date', '<=', self.date_to),
                ('country_code', '=', 'DO'),
            ])
        
        # Crear líneas del reporte
        line_vals = []
        for invoice in invoices:
            # Calcular montos
            amount_untaxed = invoice.amount_untaxed
            itbis_amount = sum(invoice.line_ids.filtered(
                lambda l: l.tax_line_id and 'ITBIS' in l.tax_line_id.name
            ).mapped('balance'))
            
            withholding_amount = sum(invoice.line_ids.filtered(
                lambda l: l.tax_line_id and 'Retención' in l.tax_line_id.name
            ).mapped('balance'))
            
            line_vals.append({
                'report_id': self.id,
                'invoice_id': invoice.id,
                'partner_id': invoice.partner_id.id,
                'ncf': invoice.l10n_latam_document_number or '',
                'invoice_date': invoice.invoice_date,
                'amount_untaxed': abs(amount_untaxed),
                'itbis_amount': abs(itbis_amount),
                'withholding_amount': abs(withholding_amount),
                'amount_total': invoice.amount_total,
            })
        
        self.env['l10n.do.dgii.report.line'].create(line_vals)
        
        self.state = 'generated'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Reporte Generado'),
                'message': _('Se generaron %d líneas para el reporte %s') % (len(line_vals), self.report_type),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_generate_txt(self):
        """Genera el archivo TXT en formato DGII."""
        self.ensure_one()
        
        if not self.line_ids:
            raise UserError(_("No hay líneas para exportar. Genere el reporte primero."))
        
        # Crear contenido del archivo según formato DGII
        lines = []
        
        for line in self.line_ids:
            # Formato específico DGII (pipe-separated)
            if self.report_type == '606':
                # Formato 606: RNC|Tipo|NCF|Fecha|Monto|ITBIS|Retencion|...
                txt_line = '|'.join([
                    line.partner_id.vat or '',
                    line.invoice_id.l10n_latam_document_type_id.code or '',
                    line.ncf or '',
                    line.invoice_date.strftime('%Y%m%d') if line.invoice_date else '',
                    str(round(line.amount_untaxed, 2)),
                    str(round(line.itbis_amount, 2)),
                    str(round(line.withholding_amount, 2)),
                    str(round(line.amount_total, 2)),
                ])
            else:
                # Formato 607: RNC|Tipo|NCF|Fecha|Monto|ITBIS|...
                txt_line = '|'.join([
                    line.partner_id.vat or '',
                    line.invoice_id.l10n_latam_document_type_id.code or '',
                    line.ncf or '',
                    line.invoice_date.strftime('%Y%m%d') if line.invoice_date else '',
                    str(round(line.amount_untaxed, 2)),
                    str(round(line.itbis_amount, 2)),
                    str(round(line.amount_total, 2)),
                ])
            
            lines.append(txt_line)
        
        # Crear archivo
        content = '\n'.join(lines)
        
        # Generar nombre del archivo
        period = self.date_from.strftime('%Y%m')
        filename = f"{self.report_type}_{self.company_id.l10n_do_rnc}_{period}.txt"
        
        # Guardar archivo
        self.txt_file = base64.b64encode(content.encode('utf-8'))
        self.txt_filename = filename
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Archivo TXT Generado'),
                'message': _('El archivo %s ha sido generado exitosamente.') % filename,
                'type': 'success',
                'sticky': False,
            }
        }

    def action_send_dgii(self):
        """Marca el reporte como enviado a la DGII."""
        self.ensure_one()
        
        if not self.txt_file:
            raise UserError(_("Debe generar el archivo TXT antes de marcarlo como enviado."))
        
        self.state = 'sent'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Reporte Enviado'),
                'message': _('El reporte ha sido marcado como enviado a la DGII.'),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_reset_to_draft(self):
        """Resetea el reporte a borrador."""
        self.state = 'draft'

    def action_cancel(self):
        """Cancela el reporte."""
        self.state = 'cancelled'


class L10nDoDgiiReportLine(models.Model):
    _name = 'l10n.do.dgii.report.line'
    _description = 'Línea de Reporte DGII'
    _order = 'invoice_date, id'

    report_id = fields.Many2one(
        'l10n.do.dgii.report',
        string='Reporte',
        required=True,
        ondelete='cascade',
        index=True,
    )
    
    invoice_id = fields.Many2one(
        'account.move',
        string='Factura',
        required=True,
        ondelete='restrict',
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Contacto',
        required=True,
    )
    
    partner_vat = fields.Char(
        string='RNC/Cédula',
        related='partner_id.vat',
        readonly=True,
    )
    
    ncf = fields.Char(
        string='NCF',
        required=True,
    )
    
    ncf_type = fields.Char(
        string='Tipo NCF',
        related='invoice_id.l10n_latam_document_type_id.code',
        readonly=True,
    )
    
    invoice_date = fields.Date(
        string='Fecha Factura',
        required=True,
    )
    
    amount_untaxed = fields.Monetary(
        string='Monto sin Impuesto',
        currency_field='currency_id',
    )
    
    itbis_amount = fields.Monetary(
        string='ITBIS',
        currency_field='currency_id',
    )
    
    withholding_amount = fields.Monetary(
        string='Retención',
        currency_field='currency_id',
    )
    
    amount_total = fields.Monetary(
        string='Monto Total',
        currency_field='currency_id',
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        related='report_id.currency_id',
        readonly=True,
    )
    
    expense_type = fields.Selection(
        related='partner_id.l10n_do_expense_type',
        string='Tipo de Gasto',
        readonly=True,
    )

