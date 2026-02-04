import requests
from lxml import html
import warnings
warnings.filterwarnings("ignore") # Ignorar warnings de SSL verify=False

def search_dgii(name):
    print(f"Buscando '{name}' en DGII...")
    try:
        session = requests.Session()
        url = "https://dgii.gov.do/app/WebApps/ConsultasWeb2/ConsultasWeb/consultas/rnc.aspx"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': url
        }
        
        # 1. GET inicial
        print("- Obteniendo tokens...")
        try:
            r1 = session.get(url, headers=headers, timeout=10, verify=False)
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Fallo conectando a DGII: {e}")
            return

        tree = html.fromstring(r1.content)
        viewstate = tree.xpath('//input[@id="__VIEWSTATE"]/@value')
        eventval = tree.xpath('//input[@id="__EVENTVALIDATION"]/@value')
        viewgen = tree.xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value')
        
        if not viewstate or not eventval:
            print("ERROR: No se pudieron obtener tokens ASP.NET")
            return

        # 2. POST búsqueda
        print("- Enviando consulta...")
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
        
        headers.update({
            'X-MicrosoftAjax': 'Delta=true',
            'X-Requested-With': 'XMLHttpRequest',
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        })
        
        r2 = session.post(url, data=payload, headers=headers, timeout=10, verify=False)
        content = r2.text
        
        # 3. Parsear
        print("- Parseando respuesta...")
        if 'id="cphMain_gvBuscRazonSocial"' in content:
            start_marker = '<table class="table text-black table-topbot table-sm-filled" cellspacing="0" rules="all" border="1" id="cphMain_gvBuscRazonSocial"'
            end_marker = '</table>'
            
            start_idx = content.find(start_marker)
            if start_idx != -1:
                end_idx = content.find(end_marker, start_idx)
                if end_idx != -1:
                    table_html = content[start_idx:end_idx + len(end_marker)]
                    tree2 = html.fromstring(table_html)
                    rows = tree2.xpath('//tr')
                    
                    found = False
                    print("\nRESULTADOS ENCONTRADOS:")
                    print("-" * 60)
                    print(f"{'RNC':<15} | {'NOMBRE':<40}")
                    print("-" * 60)
                    for row in rows:
                        cols = row.xpath('./td')
                        if len(cols) >= 2:
                            rnc_val = cols[0].text_content().strip()
                            name_val = cols[1].text_content().strip()
                            if rnc_val and name_val:
                                print(f"{rnc_val:<15} | {name_val[:40]}")
                                found = True
                    if not found:
                         print("Tabla encontrada pero sin filas de datos.")
                else:
                    print("No se encontró cierre de tabla.")
            else:
                 print("No se encontró inicio de tabla en la respuesta.")
        else:
            print("No se encontró la tabla de resultados en el HTML.")
            # print("DEBUG CONTENT SAMPLE:", content[:500])

    except Exception as e:
        print(f"ERROR EXCEPTION: {e}")

if __name__ == "__main__":
    search_dgii("Tienda")
