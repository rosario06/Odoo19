# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


class L10nDoDgiiReportWizard(models.TransientModel):
    _name = 'l10n.do.dgii.report.wizard'
    _description = 'Wizard para Generar Reportes DGII'

    report_type = fields.Selection(
        [
            ('606', 'Reporte 606 - Compras'),
            ('607', 'Reporte 607 - Ventas'),
        ],
        string='Tipo de Reporte',
        required=True,
        default='606',
    )
    
    period_type = fields.Selection(
        [
            ('month', 'Mes Específico'),
            ('custom', 'Período Personalizado'),
        ],
        string='Tipo de Período',
        default='month',
        required=True,
    )
    
    year = fields.Integer(
        string='Año',
        default=lambda self: date.today().year,
        required=True,
    )
    
    month = fields.Selection(
        [
            ('1', 'Enero'),
            ('2', 'Febrero'),
            ('3', 'Marzo'),
            ('4', 'Abril'),
            ('5', 'Mayo'),
            ('6', 'Junio'),
            ('7', 'Julio'),
            ('8', 'Agosto'),
            ('9', 'Septiembre'),
            ('10', 'Octubre'),
            ('11', 'Noviembre'),
            ('12', 'Diciembre'),
        ],
        string='Mes',
        default=lambda self: str(date.today().month),
    )
    
    date_from = fields.Date(
        string='Fecha Desde',
        default=lambda self: date.today().replace(day=1),
    )
    
    date_to = fields.Date(
        string='Fecha Hasta',
        default=lambda self: date.today(),
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company,
    )

    @api.onchange('period_type', 'year', 'month')
    def _onchange_period(self):
        """Calcula las fechas según el período seleccionado."""
        if self.period_type == 'month' and self.year and self.month:
            # Primer día del mes
            self.date_from = date(self.year, int(self.month), 1)
            # Último día del mes
            next_month = self.date_from + relativedelta(months=1)
            self.date_to = next_month - relativedelta(days=1)

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        """Valida que las fechas sean correctas."""
        for wizard in self:
            if wizard.date_from > wizard.date_to:
                raise ValidationError(_("La fecha 'Desde' debe ser anterior a la fecha 'Hasta'."))

    def action_generate_report(self):
        """Genera el reporte DGII."""
        self.ensure_one()
        
        # Validar que la empresa tenga RNC
        if not self.company_id.l10n_do_rnc:
            raise UserError(_("La empresa %s no tiene un RNC configurado. Por favor configure el RNC en Ajustes → Empresas.") % self.company_id.name)
        
        # Generar nombre del reporte
        if self.period_type == 'month':
            period_name = f"{dict(self._fields['month'].selection)[self.month]} {self.year}"
        else:
            period_name = f"{self.date_from.strftime('%d/%m/%Y')} - {self.date_to.strftime('%d/%m/%Y')}"
        
        report_name = f"Reporte {self.report_type} - {period_name}"
        
        # Crear el reporte
        report = self.env['l10n.do.dgii.report'].create({
            'name': report_name,
            'company_id': self.company_id.id,
            'report_type': self.report_type,
            'date_from': self.date_from,
            'date_to': self.date_to,
        })
        
        # Generar automáticamente las líneas
        report.action_generate_report()
        
        # Abrir el reporte creado
        return {
            'name': _('Reporte DGII'),
            'type': 'ir.actions.act_window',
            'res_model': 'l10n.do.dgii.report',
            'res_id': report.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_generate_multiple_reports(self):
        """Genera reportes 606 y 607 simultáneamente."""
        self.ensure_one()
        
        reports = []
        
        for report_type in ['606', '607']:
            # Generar nombre del reporte
            if self.period_type == 'month':
                period_name = f"{dict(self._fields['month'].selection)[self.month]} {self.year}"
            else:
                period_name = f"{self.date_from.strftime('%d/%m/%Y')} - {self.date_to.strftime('%d/%m/%Y')}"
            
            report_name = f"Reporte {report_type} - {period_name}"
            
            # Crear el reporte
            report = self.env['l10n.do.dgii.report'].create({
                'name': report_name,
                'company_id': self.company_id.id,
                'report_type': report_type,
                'date_from': self.date_from,
                'date_to': self.date_to,
            })
            
            # Generar automáticamente las líneas
            report.action_generate_report()
            reports.append(report.id)
        
        # Abrir lista de reportes creados
        return {
            'name': _('Reportes DGII Generados'),
            'type': 'ir.actions.act_window',
            'res_model': 'l10n.do.dgii.report',
            'domain': [('id', 'in', reports)],
            'view_mode': 'tree,form',
            'target': 'current',
        }

