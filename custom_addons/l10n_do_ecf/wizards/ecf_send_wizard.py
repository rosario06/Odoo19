# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class EcfSendWizard(models.TransientModel):
    _name = 'ecf.send.wizard'
    _description = 'Wizard de Envío de e-CF'

    invoice_ids = fields.Many2many(
        'account.move',
        string='Facturas',
        required=True
    )
    
    invoice_count = fields.Integer(
        string='Cantidad de Facturas',
        compute='_compute_invoice_count'
    )
    
    generate_xml = fields.Boolean(
        string='Generar XML',
        default=True
    )
    
    sign_xml = fields.Boolean(
        string='Firmar XML',
        default=True
    )
    
    send_to_dgii = fields.Boolean(
        string='Enviar a DGII',
        default=True
    )

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for wizard in self:
            wizard.invoice_count = len(wizard.invoice_ids)

    def action_process(self):
        """Procesa las facturas seleccionadas"""
        self.ensure_one()
        
        if not self.invoice_ids:
            raise UserError(_('Debe seleccionar al menos una factura.'))
        
        # Verificar que las facturas cumplan requisitos
        invalid_invoices = self.invoice_ids.filtered(lambda inv: not inv.can_send_ecf)
        if invalid_invoices:
            raise UserError(_(
                'Las siguientes facturas no cumplen los requisitos para e-CF:\n%s'
            ) % '\n'.join(invalid_invoices.mapped('name')))
        
        results = {
            'success': [],
            'errors': [],
        }
        
        for invoice in self.invoice_ids:
            try:
                # Crear documento e-CF si no existe
                if not invoice.ecf_document_id:
                    invoice.action_create_ecf_document()
                
                ecf_doc = invoice.ecf_document_id
                
                # Generar XML
                if self.generate_xml and not ecf_doc.xml_content:
                    ecf_doc.action_generate_xml()
                
                # Firmar XML
                if self.sign_xml and not ecf_doc.xml_signed:
                    ecf_doc.action_sign_xml()
                
                # Enviar a DGII
                if self.send_to_dgii:
                    ecf_doc.action_send_to_dgii()
                
                results['success'].append(invoice.name)
                
            except Exception as e:
                results['errors'].append({
                    'invoice': invoice.name,
                    'error': str(e)
                })
        
        # Mostrar resultados
        message = _('Procesamiento completado:\n')
        message += _('✓ Exitosos: %d\n') % len(results['success'])
        message += _('✗ Errores: %d\n') % len(results['errors'])
        
        if results['errors']:
            message += _('\nErrores:\n')
            for error in results['errors']:
                message += _('• %s: %s\n') % (error['invoice'], error['error'])
        
        notification_type = 'success' if not results['errors'] else 'warning'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Envío de e-CF'),
                'message': message,
                'type': notification_type,
                'sticky': True,
            }
        }

