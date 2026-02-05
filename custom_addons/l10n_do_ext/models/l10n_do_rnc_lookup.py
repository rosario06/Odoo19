# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import requests
import logging

_logger = logging.getLogger(__name__)

class L10nDoRncLookup(models.TransientModel):
    _name = 'l10n_do_ext.rnc.lookup'
    _description = 'Puente de Autocompletado RNC'

    name = fields.Char('Nombre o Razón Social')
    vat = fields.Char('RNC / Cédula')
    
    def _search_dgii_by_name(self, name):
        """
        Realiza scraping de la página de consulta de la DGII para buscar por razón social.
        """
        try:
            import requests
            from lxml import html
            session = requests.Session()
            url = "https://dgii.gov.do/app/WebApps/ConsultasWeb2/ConsultasWeb/consultas/rnc.aspx"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': url
            }
            
            # 1. GET inicial para tokens de ASP.NET
            try:
                r1 = session.get(url, headers=headers, timeout=4, verify=False)
            except:
                return [] # Fallo silencioso si no hay conexión
                
            if r1.status_code != 200:
                return []
                
            tree = html.fromstring(r1.content)
            viewstate = tree.xpath('//input[@id="__VIEWSTATE"]/@value')
            eventval = tree.xpath('//input[@id="__EVENTVALIDATION"]/@value')
            viewgen = tree.xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value')
            
            if not viewstate or not eventval:
                return []
                
            # 2. POST de búsqueda
            # Nota: No enviamos X-MicrosoftAjax para tratar de forzar una respuesta full-page o manejar el parcial
            # La respuesta provista por el usuario sugiere que el servidor siempre responde con pipes si detecta AJAX
            # o quizás es el comportamiento por defecto del evento.
            # Intentaremos parsear la respuesta pipe-delimited si no es HTML puro.
            
            payload = {
                'ctl00$smMain': 'ctl00$cphMain$upBusqueda|ctl00$cphMain$btnBuscarPorRazonSocial',
                'ctl00$cphMain$txtRNCCedula': '',
                'ctl00$cphMain$txtRazonSocial': name,
                'ctl00$cphMain$hidActiveTab': 'razonsocial',
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': viewstate[0],
                '__VIEWSTATEGENERATOR': viewgen[0] if viewgen else '',
                '__EVENTVALIDATION': eventval[0],
                '__ASYNCPOST': 'true',
                'ctl00$cphMain$btnBuscarPorRazonSocial': 'BUSCAR'
            }
            
            # Headers necesarios para simular la petición AJAX del UpdatePanel
            headers.update({
                'X-MicrosoftAjax': 'Delta=true',
                'X-Requested-With': 'XMLHttpRequest',
                'Cache-Control': 'no-cache',
            })
            
            r2 = session.post(url, data=payload, headers=headers, timeout=8, verify=False)
            
            content = r2.text
            
            # 3. Parsear respuesta (Pipe-delimited o HTML)
            # Buscamos el fragmento de tabla dentro de la respuesta
            # La respuesta típica es: length|type|id|content|...
            
            # Una forma robusta es buscar simplemente el HTML de la tabla en el texto crudo
            # ya que el formato pipe solo envuelve el HTML.
            
            if 'id="cphMain_gvBuscRazonSocial"' in content:
                # Extraer desde el inicio de la tabla hasta el fin de la tabla
                start_marker = '<table class="table text-black table-topbot table-sm-filled" cellspacing="0" rules="all" border="1" id="cphMain_gvBuscRazonSocial"'
                end_marker = '</table>'
                
                start_idx = content.find(start_marker)
                if start_idx != -1:
                    # Encontrar el cierre de la tabla
                    # Esto es un aproxima simple, asumimos que no hay tablas anidadas complejas
                    end_idx = content.find(end_marker, start_idx)
                    if end_idx != -1:
                        table_html = content[start_idx:end_idx + len(end_marker)]
                        
                        tree2 = html.fromstring(table_html)
                        rows = tree2.xpath('//tr') # Ya estamos en la tabla
                        
                        results = []
                        for row in rows:
                            cols = row.xpath('./td')
                            # Ignorar encabezados (th)
                            if len(cols) >= 2:
                                rnc_val = cols[0].text_content().strip()
                                name_val = cols[1].text_content().strip()
                                # Limpiar datos extra
                                if rnc_val and name_val:
                                    vat_clean = rnc_val.replace('-', '').replace(' ', '')
                                    results.append({
                                        'name': name_val,
                                        'vat': vat_clean
                                    })
                                    if len(results) >= 8: break
                        return results
            
            return []
            
        except Exception as e:
            _logger.warning(f"DGII Scraping Error: {e}")
            return []

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        """
        Sobrescribe la búsqueda interna para inyectar resultados de la API externa.
        """
        domain = domain or []
        
        # Si hay término de búsqueda, intentar llamar a la API
        if name and len(name) > 2:
            _logger.info(f"RNC LOOKUP: Buscando término: '{name}'")
            try:
                results = []
                # 1. Si es número: Búsqueda por RNC directa
                if name.isdigit() and len(name) in (9, 11):
                    try:
                        url = f"https://api.marcos.do/rnc/{name}"
                        response = requests.get(url, timeout=3)
                        if response.status_code == 200:
                            data = response.json()
                            if data.get('name'):
                                results.append({
                                    'name': data.get('name'),
                                    'vat': name
                                })
                    except:
                        pass
                
                # 2. Búsqueda por NOMBRE en DGII Oficial (Scraping)
                if not results:
                    dgii_results = self._search_dgii_by_name(name)
                    if dgii_results:
                        results.extend(dgii_results)
                
                # Inyectar resultados externos
                if results:
                    _logger.info(f"RNC LOOKUP: Encontrados {len(results)} resultados externos.")
                    # Crear registros transitorios reales
                    ids = []
                    for res_data in results:
                        # Buscar si ya existe temporalmente
                        # Limpiamos el VAT antes de buscar/crear
                        vat_clean = res_data['vat'].replace('-', '').replace(' ', '')
                        
                        existing = self.search([('vat', '=', vat_clean)], limit=1)
                        if not existing:
                            new_rec = self.create({
                                'name': res_data['name'],
                                'vat': vat_clean
                            })
                            ids.append(new_rec.id)
                        else:
                            ids.append(existing.id)
                    
                    # Agregar los nuevos IDs al dominio para que aparezcan
                    if ids:
                        domain = ['|', ('id', 'in', ids)] + domain
                        
            except Exception as e:
                _logger.warning(f"Error en autocompletado RNC: {e}")

                # Ejecutar búsqueda estándar (ahora incluirá los registros recién creados)
                # Nota: TransientModel no siempre tiene _name_search en super(), así que usamos search() simple
                return self.search(domain, limit=limit, order=order).name_get()
            except Exception as e:
                _logger.error(f"Error CRITICO en _name_search: {e}")
                return []
        
        # Fallback estándar
        return self.search(domain, limit=limit, order=order).name_get()

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """
        Sobrescribe name_search clásico para asegurar compatibilidad.
        """
        _logger.info(f"RNC LOOKUP: name_search llamado con '{name}'")
        # Forzar la llamada a nuestra lógica interna si hay nombre
        if name:
            # Llamamos a _name_search para que haga la magia (él ya hace el log)
            self._name_search(name, args, operator, limit)
        return super().name_search(name, args, operator, limit)
