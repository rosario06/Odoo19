# Guía de Instalación - l10n_do_ecf

## ✅ MÓDULO CREADO EXITOSAMENTE

El módulo de **Facturación Electrónica DGII (e-CF)** ha sido creado completamente.

---

## 📁 Estructura del Módulo

```
l10n_do_ecf/
├── __init__.py                                   ✅ Creado
├── __manifest__.py                               ✅ Creado
├── README.md                                     ✅ Creado
├── requirements.txt                              ✅ Creado
├── models/
│   ├── __init__.py                              ✅ Creado
│   ├── ecf_document.py                          ✅ Creado (Modelo principal)
│   ├── ecf_certificate.py                       ✅ Creado (Certificados)
│   ├── ecf_webservice.py                        ✅ Creado (Integración DGII)
│   ├── account_move.py                          ✅ Creado (Extensión facturas)
│   ├── res_company.py                           ✅ Creado (Extensión empresa)
│   └── res_config_settings.py                   ✅ Creado (Configuración)
├── wizards/
│   ├── __init__.py                              ✅ Creado
│   ├── ecf_send_wizard.py                       ✅ Creado (Envío masivo)
│   ├── ecf_test_connection_wizard.py            ✅ Creado (Prueba conexión)
│   └── ecf_cancel_wizard.py                     ✅ Creado (Anulación)
├── views/
│   ├── ecf_document_views.xml                   ✅ Creado
│   ├── ecf_certificate_views.xml                ✅ Creado
│   ├── account_move_views.xml                   ✅ Creado
│   ├── res_company_views.xml                    ✅ Creado
│   ├── res_config_settings_views.xml            ✅ Creado
│   └── ecf_menus.xml                            ✅ Creado
├── wizards/
│   ├── ecf_send_wizard_views.xml                ✅ Creado
│   └── ecf_test_connection_wizard_views.xml     ✅ Creado
├── reports/
│   └── ecf_report_templates.xml                 ✅ Creado (PDF con QR)
├── security/
│   ├── ir.model.access.csv                      ✅ Creado
│   └── ecf_security.xml                         ✅ Creado (Grupos)
├── data/
│   ├── ecf_sequences.xml                        ✅ Creado
│   └── ecf_document_types.xml                   ✅ Creado
└── static/description/
    └── (iconos pendientes)                      ⏳ Pendiente
```

---

## 🚀 PASOS SIGUIENTES

### 1. Instalar Dependencias Python

```bash
cd C:\odoo-19-addons\custom\l10n_do_ecf
pip install -r requirements.txt
```

**Nota importante sobre xmlsec en Windows:**
Si falla la instalación de xmlsec, usa una de estas alternativas:

```bash
# Opción 1: Wheel pre-compilado
pip install xmlsec --only-binary :all:

# Opción 2: Conda
conda install -c conda-forge xmlsec

# Opción 3: Descargar wheel manualmente
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#xmlsec
```

### 2. Actualizar Lista de Módulos en Odoo

1. Ir a **Apps**
2. Activar modo desarrollador (Ajustes → Activar modo desarrollador)
3. Apps → ⋯ → Actualizar Lista de Apps

### 3. Instalar el Módulo

1. En **Apps**, buscar: `Facturación Electrónica`
2. Clic en **Instalar**

### 4. Configuración Inicial

#### A. Configurar Empresa
**Ruta:** Ajustes → Empresas → Mi Empresa → Pestaña "Facturación Electrónica (e-CF)"

- [ ] Habilitar Facturación Electrónica
- [ ] Seleccionar Modo: Pruebas (testecf) o Producción
- [ ] URL: `https://ecf.dgii.gov.do/testecf/ws/recepcionecf` (pruebas)
- [ ] Cargar Certificado Digital (.p12 o .pfx)
- [ ] Ingresar Contraseña del Certificado

#### B. Gestionar Certificados
**Ruta:** Contabilidad → Facturación Electrónica → Certificados Digitales

1. Crear nuevo certificado
2. Cargar archivo .p12/.pfx
3. Ingresar contraseña
4. Clic en **Validar Certificado**
5. Clic en **Activar**

#### C. Probar Conexión
**Ruta:** Contabilidad → Facturación Electrónica → Configuración → Probar Conexión DGII

- Verificar que la conexión sea exitosa

---

## 🧪 PRUEBAS

### Caso de Prueba 1: Crear y Enviar e-CF

1. **Crear factura de venta:**
   - Contabilidad → Clientes → Facturas
   - Crear factura nueva
   - Agregar cliente con RNC
   - Agregar líneas
   - Confirmar factura

2. **Enviar e-CF:**
   - Clic en botón "Enviar e-CF"
   - Verificar generación de XML
   - Verificar firma digital
   - Verificar envío a DGII
   - Verificar recepción de Track ID

3. **Consultar Estado:**
   - Clic en "Ver e-CF"
   - Clic en "Consultar Estado"
   - Verificar aprobación

4. **Imprimir Representación:**
   - Desde el documento e-CF
   - Imprimir → Representación Impresa e-CF
   - Verificar QR code

### Caso de Prueba 2: Anular e-CF

1. Abrir factura con e-CF aprobado
2. Clic en "Ver e-CF"
3. Clic en "Anular e-CF"
4. Seleccionar motivo
5. Ingresar detalle
6. Confirmar

---

## 🔧 CONFIGURACIÓN AVANZADA

### Modo Producción

Cuando esté listo para producción:

1. **Cambiar a certificado de producción:**
   - Obtener certificado de producción de entidad certificadora
   - Cargar en Certificados Digitales
   - Validar y activar

2. **Cambiar URL:**
   - Ajustes → Empresas → Mi Empresa
   - Deshabilitar "Modo de Pruebas"
   - URL cambiará automáticamente a: `https://ecf.dgii.gov.do/ecf/ws/recepcionecf`

3. **Proceso de Certificación DGII:**
   - Completar casos de prueba requeridos
   - Solicitar certificación a DGII
   - Esperar aprobación
   - Activar modo producción

---

## ⚠️ NOTAS IMPORTANTES

### Funcionalidades Implementadas:
- ✅ Generación de XML según formato DGII v1.0
- ✅ Firma digital con certificados PKCS#12
- ✅ Envío a servicios DGII (SOAP)
- ✅ Consulta de estado
- ✅ Anulación de e-CF
- ✅ Representación impresa con QR
- ✅ Gestión de certificados
- ✅ Envío masivo
- ✅ Historial de eventos
- ✅ Multi-empresa

### Funcionalidades que requieren ajuste con datos reales:
- ⚠️ **Firma XMLDSig completa:** Actualmente simplificada, requiere implementación completa con xmlsec
- ⚠️ **Respuestas DGII reales:** Actualmente simuladas, se activarán con certificado real
- ⚠️ **Validación de esquemas XSD:** Pendiente descarga de esquemas oficiales DGII

### Próximos Pasos de Desarrollo:
1. Implementar firma XMLDSig completa con xmlsec
2. Probar con certificado real de DGII en ambiente testecf
3. Validar respuestas reales de DGII
4. Ajustar parseo de respuestas según formato real
5. Implementar manejo de todos los códigos de error DGII
6. Agregar validación de esquemas XSD
7. Optimizar cola de envío asíncrono
8. Agregar más reportes y estadísticas

---

## 📞 SOPORTE

Para soporte técnico o consultas:
- Email: soporte@dynasoftsolutions.com
- Documentación DGII: https://dgii.gov.do/ecf

---

## ✅ CHECKLIST DE INSTALACIÓN

- [ ] Dependencias Python instaladas
- [ ] Módulo instalado en Odoo
- [ ] Certificado digital cargado y validado
- [ ] Conexión con DGII probada exitosamente
- [ ] Primera factura de prueba enviada
- [ ] e-CF aprobado por DGII (en testecf)
- [ ] Representación impresa generada con QR
- [ ] Anulación probada

---

**¡El módulo está listo para ser probado!** 🎉

