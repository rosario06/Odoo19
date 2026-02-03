# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import base64
from io import BytesIO
from datetime import datetime

# Importación condicional de qrcode
try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False


class L10nDoNcfSequence(models.Model):
    _name = 'l10n.do.ncf.sequence'
    _description = 'Gestión Avanzada de Secuencias NCF'
    _order = 'sequence_type_id, expiration_date'

    name = fields.Char(
        string='Nombre',
        required=True,
    )
    
    sequence_type_id = fields.Many2one(
        'l10n_latam.document.type',
        string='Tipo de Documento',
        required=True,
        domain=[('country_id.code', '=', 'DO')],
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company,
    )
    
    range_from = fields.Char(
        string='NCF Desde',
        required=True,
        help='Ejemplo: B0100000001',
    )
    
    range_to = fields.Char(
        string='NCF Hasta',
        required=True,
        help='Ejemplo: B0100001000',
    )
    
    next_number = fields.Integer(
        string='Siguiente Número',
        default=1,
        required=True,
    )
    
    expiration_date = fields.Date(
        string='Fecha de Vencimiento',
        help='Fecha de vencimiento autorizada por la DGII',
    )
    
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('active', 'Activo'),
        ('expired', 'Vencido'),
        ('depleted', 'Agotado'),
    ], string='Estado', default='draft', required=True)
    
    remaining = fields.Integer(
        string='NCF Restantes',
        compute='_compute_remaining',
        store=True,
    )
    
    usage_percentage = fields.Float(
        string='% Uso',
        compute='_compute_remaining',
        store=True,
    )

    @api.depends('range_from', 'range_to', 'next_number')
    def _compute_remaining(self):
        """Calcula los NCF restantes y el porcentaje de uso."""
        for sequence in self:
            try:
                from_number = int(sequence.range_from[-8:]) if sequence.range_from else 0
                to_number = int(sequence.range_to[-8:]) if sequence.range_to else 0
                total = to_number - from_number + 1
                used = sequence.next_number - from_number
                sequence.remaining = total - used if used >= 0 else total
                sequence.usage_percentage = (used / total * 100) if total > 0 else 0
            except (ValueError, IndexError):
                sequence.remaining = 0
                sequence.usage_percentage = 0

    @api.constrains('range_from', 'range_to')
    def _check_ncf_range(self):
        """Valida el formato y rango de NCF."""
        for sequence in self:
            if sequence.range_from and sequence.range_to:
                try:
                    prefix_from = sequence.range_from[:3]
                    prefix_to = sequence.range_to[:3]
                    
                    if prefix_from != prefix_to:
                        raise ValidationError(_("Los prefijos de los NCF deben ser iguales."))
                    
                    number_from = int(sequence.range_from[3:])
                    number_to = int(sequence.range_to[3:])
                    
                    if number_from >= number_to:
                        raise ValidationError(_("El NCF inicial debe ser menor que el final."))
                    
                except (ValueError, IndexError):
                    raise ValidationError(_("Formato de NCF inválido. Use el formato: B0100000001"))

    def action_activate(self):
        """Activa la secuencia."""
        self.ensure_one()
        if not self.expiration_date:
            raise UserError(_("Debe configurar una fecha de vencimiento."))
        if self.expiration_date < fields.Date.today():
            raise UserError(_("La fecha de vencimiento debe ser futura."))
        
        self.state = 'active'

    def get_next_ncf(self):
        """Obtiene el siguiente NCF de la secuencia."""
        self.ensure_one()
        
        # Validar estado
        if self.state != 'active':
            raise UserError(_("La secuencia no está activa."))
        
        # Validar vencimiento
        if self.expiration_date and self.expiration_date < fields.Date.today():
            self.state = 'expired'
            raise UserError(_("La secuencia está vencida."))
        
        # Calcular siguiente NCF
        try:
            prefix = self.range_from[:3]
            from_number = int(self.range_from[3:])
            to_number = int(self.range_to[3:])
            
            current = from_number + self.next_number - 1
            
            if current > to_number:
                self.state = 'depleted'
                raise UserError(_("La secuencia está agotada. Contacte a la DGII para obtener un nuevo rango."))
            
            # Incrementar contador
            self.next_number += 1
            
            # Formatear NCF
            ncf = f"{prefix}{str(current).zfill(8)}"
            
            # Si llegamos al final, marcar como agotada
            if self.next_number > (to_number - from_number + 1):
                self.state = 'depleted'
            
            return ncf
            
        except (ValueError, IndexError) as e:
            raise UserError(_("Error al generar NCF: %s") % str(e))


class L10nDoQRGenerator(models.AbstractModel):
    _name = 'l10n.do.qr.generator'
    _description = 'Generador de Códigos QR para e-CF'

    def generate_qr_code(self, invoice):
        """Genera el código QR para una factura según especificaciones DGII."""
        if not QRCODE_AVAILABLE:
            raise UserError(_("La librería 'qrcode' no está instalada. Instálela con: pip install qrcode[pil]"))
        
        # Preparar datos del QR según especificaciones DGII
        qr_data = f"RNC:{invoice.company_id.l10n_do_rnc}|NCF:{invoice.l10n_latam_document_number or ''}|Fecha:{invoice.invoice_date}|Monto:{invoice.amount_total:.2f}"
        
        # Generar QR
        qr = qrcode.QRCode(
            version=5,
            error_correction=qrcode.constants.ERROR_CORRECT_Q,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Crear imagen
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_image = base64.b64encode(buffer.getvalue())
        
        return qr_image

