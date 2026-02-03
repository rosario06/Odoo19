# República Dominicana - Facturación Electrónica DGII (e-CF)

## Descripción

Módulo completo de **Facturación Electrónica DGII (e-CF)** para República Dominicana en Odoo 19.

Implementa la integración total con los servicios de Facturación Electrónica de la DGII según las especificaciones técnicas v1.0.

## Características

### ✅ Generación de e-CF
- Generación automática de XML según formato DGII v1.0
- Soporte para todos los tipos de e-CF (31-47)
- Validación de esquemas XSD
- Estructura completa de documentos electrónicos

### ✅ Firma Digital
- Firma digital XML con certificados PKCS#12
- Soporte para certificados .p12 y .pfx
- Validación de certificados
- Alertas de vencimiento

### ✅ Integración DGII
- Envío automático a servicios DGII (SOAP/WSDL)
- Recepción de Acuse de Recibo
- Aprobación Comercial
- Consulta de estado en tiempo real
- Anulación de e-CF
- Ambiente de pruebas (testecf)
- Ambiente de producción

### ✅ Representación Impresa
- PDF con código QR automático
- Formato según modelos ilustrativos DGII
- Información de seguridad y validación

### ✅ Gestión de Certificados
- Administración de certificados digitales
- Validación automática
- Control de vencimiento
- Multi-empresa

### ✅ Funcionalidades Avanzadas
- Cola de envío asíncrono
- Manejo de errores y reintentos
- Historial completo de eventos
- Estadísticas y reportes
- Notificaciones automáticas

## Requisitos

### Módulos Odoo
- `base`
- `account`
- `l10n_do`
- `l10n_do_ext`
- `l10n_latam_invoice_document`

### Dependencias Python
```bash
pip install zeep==4.2.1
pip install xmlsec==1.3.13
pip install lxml==5.1.0
pip install cryptography==42.0.5
pip install pyOpenSSL==24.1.0
pip install requests==2.31.0
pip install qrcode==7.4.2
pip install pillow==10.2.0
pip install xmlschema==3.0.2
```

### Certificado Digital
- Certificado PKCS#12 (.p12 o .pfx)
- Emitido por entidad certificadora autorizada por DGII
- Contraseña del certificado

### Registro DGII
- Cuenta en portal DGII
- Usuario administrador e-CF
- RNC autorizado para facturación electrónica

## Instalación

1. **Instalar dependencias Python:**
```bash
cd C:\odoo-19-addons\custom\l10n_do_ecf
pip install -r requirements.txt
```

2. **Actualizar lista de módulos en Odoo:**
   - Apps → Actualizar lista de Apps

3. **Instalar módulo:**
   - Buscar "República Dominicana - Facturación Electrónica"
   - Clic en "Instalar"

## Configuración

### 1. Configuración de Empresa

Ve a **Ajustes → Empresas → Mi Empresa → Pestaña "Facturación Electrónica (e-CF)"**:

- ✓ Habilitar Facturación Electrónica
- ✓ Seleccionar Modo (Pruebas/Producción)
- ✓ URL de servicios DGII
- ✓ Cargar Certificado Digital (.p12/.pfx)
- ✓ Contraseña del Certificado
- ✓ Código de Seguridad (si aplica)

### 2. Certificados Digitales

Ve a **Contabilidad → Configuración → Certificados e-CF**:

1. Crear nuevo certificado
2. Cargar archivo .p12/.pfx
3. Ingresar contraseña
4. Clic en "Validar Certificado"
5. Clic en "Activar"

### 3. Probar Conexión

Ve a **Ajustes → Empresas → Mi Empresa**:

- Clic en "Probar Conexión e-CF"
- Verificar mensaje de éxito

## Uso

### Enviar e-CF desde Factura

1. Crear y confirmar factura de venta
2. Clic en "Enviar e-CF"
3. Confirmar envío
4. Esperar aprobación DGII

### Consultar Estado

1. Abrir factura con e-CF
2. Clic en "Ver e-CF"
3. Clic en "Consultar Estado"

### Anular e-CF

1. Abrir factura con e-CF aprobado
2. Clic en "Ver e-CF"
3. Clic en "Anular e-CF"
4. Seleccionar motivo
5. Confirmar anulación

### Envío Masivo

1. Ve a **Contabilidad → Facturación Electrónica → Documentos e-CF**
2. Seleccionar documentos
3. **Acción → Enviar a DGII**

## Proceso de Certificación DGII

### Fase 1: Pruebas (testecf)

1. Configurar modo "Pruebas"
2. Solicitar certificado de prueba a DGII
3. Generar facturas de prueba
4. Enviar a ambiente testecf
5. Validar respuestas

### Fase 2: Certificación

1. Completar casos de prueba DGII
2. Solicitar certificación
3. DGII valida implementación
4. Recibir aprobación

### Fase 3: Producción

1. Configurar modo "Producción"
2. Cambiar a certificado de producción
3. URL de producción
4. Facturación real

## Tipos de e-CF Soportados

| Código | Tipo de Documento |
|--------|-------------------|
| 31 | e-Factura de Crédito Fiscal |
| 32 | e-Factura de Consumo |
| 33 | e-Nota de Débito |
| 34 | e-Nota de Crédito |
| 43 | e-Factura de Gastos Menores |
| 44 | e-Factura de Regímenes Especiales |
| 45 | e-Factura Gubernamental |
| 46 | e-Factura de Exportación |
| 47 | e-Factura para Pagos al Exterior |

## Estados de e-CF

- **Borrador:** e-CF creado, pendiente de generar XML
- **Por Enviar:** XML generado, listo para firmar
- **Enviando:** En proceso de envío a DGII
- **Enviado:** Enviado a DGII, esperando respuesta
- **Aprobado:** Aprobado por DGII, e-NCF asignado
- **Rechazado:** Rechazado por DGII
- **Anulado:** Anulado en DGII
- **Error:** Error en el proceso

## Troubleshooting

### Error: "No se puede conectar a DGII"
- Verificar conexión a Internet
- Verificar firewall/proxy
- Verificar URL de servicios
- Probar en navegador: https://ecf.dgii.gov.do/testecf

### Error: "Certificado inválido"
- Verificar contraseña
- Verificar que no esté vencido
- Verificar formato (.p12 o .pfx)
- Validar con: `openssl pkcs12 -info -in certificado.p12`

### Error: "RNC no autorizado"
- Verificar que el RNC esté registrado en DGII
- Solicitar autorización para e-CF en portal DGII

### Error al instalar xmlsec en Windows
```bash
# Opción 1: Usar wheel pre-compilado
pip install xmlsec --only-binary :all:

# Opción 2: Usar conda
conda install -c conda-forge xmlsec
```

## Soporte

- **Documentación DGII:** https://dgii.gov.do/ecf
- **Portal DGII:** https://dgii.gov.do
- **Soporte Técnico:** soporte@dynasoftsolutions.com

## Licencia

LGPL-3

## Autor

**Dynasoft Solutions**
- Website: https://www.dynasoftsolutions.com

## Versión

19.0.1.0.0

## Changelog

### 1.0.0 (2025-10-19)
- ✓ Implementación inicial
- ✓ Generación de XML e-CF
- ✓ Firma digital
- ✓ Integración DGII
- ✓ Gestión de certificados
- ✓ Envío masivo
- ✓ Representación impresa con QR
- ✓ Anulación de e-CF
- ✓ Multi-empresa

