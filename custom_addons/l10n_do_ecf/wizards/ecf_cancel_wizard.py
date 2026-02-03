# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EcfCancelWizard(models.TransientModel):
    _name = 'ecf.cancel.wizard'
    _description = 'Wizard de Anulación de e-CF'

    document_id = fields.Many2one(
        'ecf.document',
        string='Documento e-CF',
        required=True,
        readonly=True
    )
    
    ecf_number = fields.Char(
        string='e-NCF',
        related='document_id.ecf_number',
        readonly=True
    )
    
    reason = fields.Selection([
        ('01', 'Error en el RNC/Cédula del cliente'),
        ('02', 'Error en el monto total'),
        ('03', 'Error en los ítems'),
        ('04', 'Duplicado'),
        ('05', 'Cliente no recibió producto/servicio'),
        ('06', 'Otros'),
    ], string='Motivo de Anulación', required=True)
    
    reason_detail = fields.Text(
        string='Detalle del Motivo',
        required=True
    )
    
    confirm = fields.Boolean(
        string='Confirmo que deseo anular este e-CF'
    )

    @api.constrains('confirm')
    def _check_confirm(self):
        for wizard in self:
            if not wizard.confirm:
                raise ValidationError(_('Debe confirmar la anulación del e-CF.'))

    def action_cancel_ecf(self):
        """Anula el e-CF en DGII"""
        self.ensure_one()
        
        if not self.confirm:
            raise UserError(_('Debe confirmar la anulación.'))
        
        if self.document_id.state != 'approved':
            raise UserError(_('Solo se pueden anular e-CF aprobados.'))
        
        try:
            # Enviar anulación a DGII
            reason_text = dict(self._fields['reason'].selection).get(self.reason)
            full_reason = f"{reason_text}: {self.reason_detail}"
            
            result = self.env['ecf.webservice'].cancel_ecf(
                self.document_id,
                full_reason
            )
            
            # Actualizar documento
            self.document_id.write({
                'state': 'cancelled',
                'cancellation_reason': full_reason,
                'cancellation_date': fields.Datetime.now(),
            })
            
            self.document_id._log_event('cancelled', _('e-CF anulado: %s') % full_reason)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('e-CF Anulado'),
                    'message': _('El e-CF %s ha sido anulado correctamente.') % self.ecf_number,
                    'type': 'success',
                    'sticky': True,
                }
            }
            
        except Exception as e:
            raise UserError(_('Error al anular e-CF: %s') % str(e))

