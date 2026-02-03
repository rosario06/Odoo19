# Inicio Rápido - l10n_do_ecf

## ✅ LISTO PARA INSTALAR

El módulo ha sido configurado para funcionar SIN xmlsec en Windows.

---

## 🚀 INSTALACIÓN (3 PASOS)

### Paso 1: Actualizar Lista de Módulos en Odoo

1. Abrir Odoo
2. Ir a **Apps**
3. Activar modo desarrollador:
   - **Ajustes → Activar modo desarrollador** (al final de la página)
4. En Apps, clic en el menú **⋯** (esquina superior derecha)
5. Seleccionar **"Actualizar Lista de Apps"**
6. Esperar que termine

### Paso 2: Instalar el Módulo

1. En **Apps**, en el buscador escribir: `Facturación Electrónica`
2. Encontrar: **"República Dominicana - Facturación Electrónica DGII (e-CF)"**
3. Clic en **Instalar**
4. Esperar que complete la instalación

### Paso 3: Verificar Instalación

1. Ir a **Contabilidad** (menú principal)
2. Verificar que aparece el menú **"Facturación Electrónica"**
3. Ir a **Facturación Electrónica → Documentos e-CF**
4. Si aparece la vista, ¡instalación exitosa! ✅

---

## ⚙️ CONFIGURACIÓN BÁSICA

### 1. Configurar Empresa

**Ruta:** Ajustes → Empresas → Mi Empresa

Ir a la pestaña **"Facturación Electrónica (e-CF)"** y configurar:

- ☑ **Habilitar e-CF**: Marcar
- ☑ **Modo de Pruebas**: Activar (para testecf)
- 📝 **URL Servicios**: `https://ecf.dgii.gov.do/testecf/ws/recepcionecf`

*Nota: El certificado se puede configurar después*

### 2. Probar Conexión (Opcional)

**Ruta:** Contabilidad → Facturación Electrónica → Configuración → Probar Conexión DGII

- Clic en **"Probar Conexión"**
- Verificar mensaje: "Conexión exitosa"

---

## 📝 PRIMERA FACTURA e-CF

### Crear Factura de Prueba

1. **Contabilidad → Clientes → Facturas**
2. Clic en **Crear**
3. Seleccionar cliente con RNC
4. Agregar productos/servicios
5. Clic en **Confirmar**

### Enviar e-CF

1. En la factura confirmada, clic en **"Enviar e-CF"**
2. Se abrirá wizard de envío
3. Verificar opciones:
   - ☑ Generar XML
   - ☑ Firmar XML (con firma simplificada)
   - ☑ Enviar a DGII
4. Clic en **"Procesar"**

### Ver Documento e-CF

1. En la factura, clic en **"Ver e-CF"**
2. Revisar:
   - XML generado
   - XML firmado (descargable)
   - Estado del documento
   - Historial de eventos

---

## ⚠️ NOTA IMPORTANTE: FIRMA DIGITAL

### Estado Actual

El módulo usa **firma simplificada** en Windows porque xmlsec no es compatible.

**¿Qué significa esto?**

- ✅ **Todo funciona** en desarrollo
- ✅ **Puedes probar** todas las funcionalidades
- ⚠️ **NO válido** para producción con DGII real

### Para Producción

Cuando vayas a producción con DGII:

1. Desplegar en **servidor Linux** (Ubuntu/Debian)
2. Instalar xmlsec:
   ```bash
   sudo apt-get install libxml2-dev libxmlsec1-dev libxmlsec1-openssl
   pip install xmlsec
   ```
3. El módulo detectará xmlsec automáticamente
4. Usará **firma XMLDSig completa**

Ver detalles en: **XMLSEC_NOTES.md**

---

## 📊 FUNCIONALIDADES DISPONIBLES

### ✅ Completamente Funcionales

1. ✅ Generación de XML e-CF
2. ✅ Gestión de certificados digitales
3. ✅ Envío a servicios DGII
4. ✅ Consulta de estado
5. ✅ Anulación de e-CF
6. ✅ Códigos QR automáticos
7. ✅ Representación impresa PDF
8. ✅ Envío masivo de facturas
9. ✅ Historial completo
10. ✅ Multi-empresa

### ⏳ Para Producción

- **Firma XMLDSig completa:** Requiere Linux + xmlsec

---

## 🎯 MENÚS PRINCIPALES

Después de instalar, encontrarás:

### Contabilidad → Facturación Electrónica
- **Documentos e-CF:** Ver todos los e-CF
- **Certificados Digitales:** Gestionar certificados
- **Configuración:**
  - Probar Conexión DGII

### En Facturas
- Botón **"Enviar e-CF"**
- Botón **"Ver e-CF"**
- Campo **"Estado e-CF"**
- Campo **"e-NCF"**

---

## 🆘 TROUBLESHOOTING

### Error: "El módulo no aparece en Apps"
**Solución:**
- Apps → ⋯ → Actualizar Lista de Apps
- Refrescar página (F5)

### Error: "No se puede conectar a DGII"
**Solución:**
- Verificar conexión a Internet
- Verificar URL: `https://ecf.dgii.gov.do/testecf/ws/recepcionecf`
- Probar en navegador

### Error: "Campo 'l10n_do_ecf_enabled' no existe"
**Solución:**
- El módulo `l10n_do_ext` debe tener los campos e-CF
- Si no los tiene, ir a: Ajustes → Empresas → Mi Empresa → Pestaña "Facturación Electrónica (e-CF)"
- Si la pestaña no existe, los campos se crearán automáticamente en la primera factura

### Advertencia: "Firma simplificada"
**Es Normal:**
- En Windows, xmlsec no está disponible
- Se usa firma simplificada
- Para producción, usar Linux

---

## 📚 DOCUMENTACIÓN COMPLETA

- **README.md:** Documentación completa del módulo
- **INSTALLATION_GUIDE.md:** Guía detallada de instalación
- **XMLSEC_NOTES.md:** Información sobre xmlsec y firma digital
- **requirements.txt:** Lista de dependencias Python

---

## 📞 SOPORTE

- Email: soporte@dynasoftsolutions.com
- DGII: https://dgii.gov.do/ecf

---

## ✅ CHECKLIST

- [ ] Módulo instalado en Odoo
- [ ] Menú "Facturación Electrónica" visible
- [ ] Empresa configurada
- [ ] Conexión DGII probada
- [ ] Primera factura creada
- [ ] e-CF enviado exitosamente
- [ ] Documento e-CF visualizado

**¡Listo para usar!** 🎉

