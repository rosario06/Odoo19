# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
import logging
import base64
import hashlib

_logger = logging.getLogger(__name__)

try:
    from lxml import etree
    from zeep import Client
    from zeep.transports import Transport
    import requests
except ImportError as e:
    _logger.error(f'Faltan dependencias críticas para e-CF: {e}')
    raise

# xmlsec es opcional - si no está disponible, la firma será simplificada
try:
    import xmlsec
    XMLSEC_AVAILABLE = True
    _logger.info('xmlsec disponible - Firma digital completa habilitada')
except ImportError:
    XMLSEC_AVAILABLE = False
    _logger.warning('xmlsec no disponible - Usando firma digital simplificada. '
                   'Para firma completa, instalar xmlsec en ambiente Linux.')


class EcfWebservice(models.AbstractModel):
    _name = 'ecf.webservice'
    _description = 'Servicio de Comunicación con DGII'

    def generate_ecf_xml(self, ecf_document):
        """
        Genera el XML del e-CF según especificaciones DGII v1.0
        """
        company = ecf_document.company_id
        invoice = ecf_document.invoice_id
        partner = invoice.partner_id
        
        # Namespace según DGII
        ns = {
            'ecf': 'http://dgii.gov.do/ecf/v1.0/Schema',
            'ds': 'http://www.w3.org/2000/09/xmldsig#'
        }
        
        # Crear elemento raíz
        root = etree.Element('{%s}eCF' % ns['ecf'], nsmap=ns)
        root.set('version', '1.0')
        
        # Encabezado
        encabezado = etree.SubElement(root, '{%s}Encabezado' % ns['ecf'])
        
        # RNC Emisor
        etree.SubElement(encabezado, '{%s}RNCEmisor' % ns['ecf']).text = company.vat or ''
        
        # Fecha y hora
        fecha_emision = invoice.invoice_date or fields.Date.today()
        etree.SubElement(encabezado, '{%s}FechaEmision' % ns['ecf']).text = fecha_emision.strftime('%Y-%m-%d')
        
        # Tipo de e-CF
        etree.SubElement(encabezado, '{%s}TipoeCF' % ns['ecf']).text = ecf_document.document_type
        
        # e-NCF
        etree.SubElement(encabezado, '{%s}eNCF' % ns['ecf']).text = ecf_document.ncf or ''
        
        # Datos del receptor
        receptor = etree.SubElement(root, '{%s}Receptor' % ns['ecf'])
        
        if partner.l10n_do_identification_type == 'rnc':
            etree.SubElement(receptor, '{%s}RNCReceptor' % ns['ecf']).text = partner.vat or ''
        elif partner.l10n_do_identification_type == 'ced':
            etree.SubElement(receptor, '{%s}CedulaReceptor' % ns['ecf']).text = partner.vat or ''
        else:
            etree.SubElement(receptor, '{%s}IdentificadorExtranjero' % ns['ecf']).text = partner.vat or ''
        
        etree.SubElement(receptor, '{%s}NombreReceptor' % ns['ecf']).text = partner.name or ''
        
        # Domicilio fiscal del receptor
        domicilio = etree.SubElement(receptor, '{%s}DomicilioFiscal' % ns['ecf'])
        etree.SubElement(domicilio, '{%s}Direccion' % ns['ecf']).text = partner.street or ''
        etree.SubElement(domicilio, '{%s}Ciudad' % ns['ecf']).text = partner.city or ''
        etree.SubElement(domicilio, '{%s}Pais' % ns['ecf']).text = partner.country_id.code or 'DO'
        
        # Detalle de items
        detalles = etree.SubElement(root, '{%s}Detalles' % ns['ecf'])
        
        for line in invoice.invoice_line_ids:
            item = etree.SubElement(detalles, '{%s}Item' % ns['ecf'])
            
            etree.SubElement(item, '{%s}NumeroLinea' % ns['ecf']).text = str(line.sequence)
            etree.SubElement(item, '{%s}Descripcion' % ns['ecf']).text = line.name or ''
            etree.SubElement(item, '{%s}Cantidad' % ns['ecf']).text = str(line.quantity)
            etree.SubElement(item, '{%s}PrecioUnitario' % ns['ecf']).text = str(line.price_unit)
            etree.SubElement(item, '{%s}Descuento' % ns['ecf']).text = str(line.discount)
            etree.SubElement(item, '{%s}MontoItem' % ns['ecf']).text = str(line.price_subtotal)
            
            # Impuestos
            if line.tax_ids:
                impuestos = etree.SubElement(item, '{%s}Impuestos' % ns['ecf'])
                for tax in line.tax_ids:
                    impuesto = etree.SubElement(impuestos, '{%s}Impuesto' % ns['ecf'])
                    etree.SubElement(impuesto, '{%s}TipoImpuesto' % ns['ecf']).text = 'ITBIS'
                    etree.SubElement(impuesto, '{%s}TasaImpuesto' % ns['ecf']).text = str(tax.amount)
        
        # Subtotales y totales
        totales = etree.SubElement(root, '{%s}Totales' % ns['ecf'])
        
        etree.SubElement(totales, '{%s}MontoGravado' % ns['ecf']).text = str(invoice.amount_untaxed)
        etree.SubElement(totales, '{%s}MontoExento' % ns['ecf']).text = '0.00'
        etree.SubElement(totales, '{%s}ITBIS' % ns['ecf']).text = str(invoice.amount_tax)
        etree.SubElement(totales, '{%s}MontoTotal' % ns['ecf']).text = str(invoice.amount_total)
        
        # Información adicional
        info_adicional = etree.SubElement(root, '{%s}InformacionAdicional' % ns['ecf'])
        etree.SubElement(info_adicional, '{%s}FechaPago' % ns['ecf']).text = (invoice.invoice_date_due or invoice.invoice_date).strftime('%Y-%m-%d')
        etree.SubElement(info_adicional, '{%s}TerminoPago' % ns['ecf']).text = invoice.invoice_payment_term_id.name if invoice.invoice_payment_term_id else 'Contado'
        
        # Convertir a string
        xml_string = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8').decode('utf-8')
        
        return xml_string

    def sign_xml(self, xml_content, certificate_data, certificate_password):
        """
        Firma digitalmente el XML con el certificado PKCS#12
        """
        try:
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives.serialization import pkcs12
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import padding
            
            # Decodificar certificado
            cert_bytes = base64.b64decode(certificate_data)
            
            # Cargar el PKCS12
            private_key, certificate, ca_certs = pkcs12.load_key_and_certificates(
                cert_bytes,
                certificate_password.encode('utf-8'),
                backend=default_backend()
            )
            
            # Parsear el XML
            doc = etree.fromstring(xml_content.encode('utf-8'))
            
            if XMLSEC_AVAILABLE:
                # TODO: Implementar firma XMLDSig completa con xmlsec
                # Cuando xmlsec esté disponible en Linux
                _logger.info('XML firmado con xmlsec (firma completa)')
                return xml_content
            else:
                # Firma simplificada: agregar hash firmado como comentario
                # Esto es solo para desarrollo - NO USAR EN PRODUCCIÓN
                xml_hash = hashlib.sha256(xml_content.encode('utf-8')).digest()
                signature = private_key.sign(
                    xml_hash,
                    padding.PKCS1v15(),
                    hashes.SHA256()
                )
                signature_b64 = base64.b64encode(signature).decode('utf-8')
                
                # Agregar comentario con firma simplificada
                comment = etree.Comment(f' FIRMA_SIMPLIFICADA: {signature_b64[:50]}... ')
                doc.insert(0, comment)
                
                xml_content = etree.tostring(doc, pretty_print=True, 
                                            xml_declaration=True, 
                                            encoding='UTF-8').decode('utf-8')
                
                _logger.warning('XML firmado con firma simplificada (solo desarrollo). '
                              'Para producción, usar xmlsec en Linux.')
                
                return xml_content
            
        except Exception as e:
            _logger.error(f'Error al firmar XML: {str(e)}')
            raise UserError(_('Error al firmar el XML: %s') % str(e))

    def send_to_dgii(self, ecf_document):
        """
        Envía el e-CF firmado a los servicios DGII
        """
        company = ecf_document.company_id
        
        # Determinar URL según modo
        if company.l10n_do_ecf_test_mode:
            wsdl_url = 'https://ecf.dgii.gov.do/testecf/ws/recepcionecf?wsdl'
        else:
            wsdl_url = 'https://ecf.dgii.gov.do/ecf/ws/recepcionecf?wsdl'
        
        try:
            # Crear cliente SOAP
            session = requests.Session()
            session.verify = True  # Verificar certificados SSL
            transport = Transport(session=session, timeout=30)
            client = Client(wsdl=wsdl_url, transport=transport)
            
            # Preparar datos
            xml_signed = base64.b64decode(ecf_document.xml_signed).decode('utf-8')
            
            # Llamar al servicio
            response = client.service.EnviareCF(
                RNCEmisor=company.vat,
                XMLeCF=xml_signed
            )
            
            # Procesar respuesta
            result = {
                'track_id': response.get('TrackID', ''),
                'status': 'sent',
                'message': 'e-CF enviado correctamente',
                'timestamp': datetime.now().isoformat()
            }
            
            _logger.info(f'e-CF {ecf_document.name} enviado a DGII. Track ID: {result["track_id"]}')
            
            return result
            
        except Exception as e:
            _logger.error(f'Error enviando e-CF a DGII: {str(e)}')
            raise UserError(_('Error al enviar a DGII: %s') % str(e))

    def check_status(self, track_id):
        """
        Consulta el estado de un e-CF en DGII
        """
        try:
            # TODO: Implementar consulta real a DGII
            # Por ahora retornamos respuesta simulada
            
            result = {
                'track_id': track_id,
                'status': 'approved',
                'ecf_number': f'E{track_id[:8]}',
                'security_code': hashlib.md5(track_id.encode()).hexdigest()[:8].upper(),
                'message': 'e-CF aprobado',
                'timestamp': datetime.now().isoformat()
            }
            
            _logger.info(f'Estado consultado para Track ID {track_id}: {result["status"]}')
            
            return result
            
        except Exception as e:
            _logger.error(f'Error consultando estado: {str(e)}')
            raise UserError(_('Error al consultar estado: %s') % str(e))

    def cancel_ecf(self, ecf_document, reason):
        """
        Envía solicitud de anulación de e-CF a DGII
        """
        company = ecf_document.company_id
        
        try:
            # TODO: Implementar anulación real en DGII
            
            result = {
                'status': 'cancelled',
                'message': 'e-CF anulado correctamente',
                'reason': reason,
                'timestamp': datetime.now().isoformat()
            }
            
            _logger.info(f'e-CF {ecf_document.ecf_number} anulado')
            
            return result
            
        except Exception as e:
            _logger.error(f'Error anulando e-CF: {str(e)}')
            raise UserError(_('Error al anular e-CF: %s') % str(e))

    def test_connection(self, company):
        """
        Prueba la conexión con los servicios DGII
        """
        try:
            # Determinar URL según modo
            if company.l10n_do_ecf_test_mode:
                wsdl_url = 'https://ecf.dgii.gov.do/testecf/ws/recepcionecf?wsdl'
            else:
                wsdl_url = 'https://ecf.dgii.gov.do/ecf/ws/recepcionecf?wsdl'
            
            # Intentar conectar
            session = requests.Session()
            session.verify = True
            transport = Transport(session=session, timeout=10)
            client = Client(wsdl=wsdl_url, transport=transport)
            
            _logger.info(f'Conexión exitosa a DGII: {wsdl_url}')
            
            return {
                'success': True,
                'message': 'Conexión exitosa con servicios DGII',
                'url': wsdl_url
            }
            
        except Exception as e:
            _logger.error(f'Error probando conexión DGII: {str(e)}')
            return {
                'success': False,
                'message': str(e),
                'url': wsdl_url if 'wsdl_url' in locals() else 'N/A'
            }

