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
    
    @api.model
    def web_search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, count_limit=None):
        """
        Sobrescribe la búsqueda web para inyectar resultados de la API externa
        cuando el usuario escribe en el campo Many2one.
        """
        # Extraer el término de búsqueda de los dominios
        search_str = ''
        for leaf in (domain or []):
            if isinstance(leaf, (list, tuple)) and leaf[0] == 'name' and leaf[1] == 'ilike':
                search_str = leaf[2]
                break
        
        # Si hay búsqueda, intentar llamar a la API
        results = []
        if search_str and len(search_str) > 3:
            try:
                # Intentamos búsqueda por RNC primero si parece un número
                if search_str.isdigit() and len(search_str) in (9, 11):
                    url = f"https://api.marcos.do/rnc/{search_str}"
                    response = requests.get(url, timeout=3)
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('name'):
                            results.append({
                                'id': -1, # ID virtual
                                'name': data.get('name'),
                                'vat': search_str,
                                'display_name': f"[{search_str}] {data.get('name')}"
                            })
                
                # Búsqueda por nombre (Simulada o vía API si existe)
                # NOTA: Si no hay API de búsqueda por nombre libre, 
                # los resultados aquí vendrán de la base de datos local y
                # opcionalmente de un servicio de scraping si se implementa.
                
            except Exception as e:
                _logger.warning(f"Error en autocompletado RNC: {e}")

        # Ejecutar búsqueda normal en el modelo transitorio (que estará vacío)
        res = super().web_search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order, count_limit=count_limit)
        
        # Inyectar resultados externos
        if results:
            # Crear registros transitorios reales para que Odoo pueda manejarlos
            # esto es necesario porque Odoo espera IDs válidos en el Many2one
            ids = []
            for res_data in results:
                existing = self.search([('vat', '=', res_data['vat'])], limit=1)
                if not existing:
                    new_rec = self.create({
                        'name': res_data['name'],
                        'vat': res_data['vat']
                    })
                    ids.append(new_rec.id)
                else:
                    ids.append(existing.id)
            
            # Re-leer los registros creados
            final_res = self.search_read([('id', 'in', ids)], fields=fields)
            return {'records': final_res, 'length': len(final_res)}

        return res
