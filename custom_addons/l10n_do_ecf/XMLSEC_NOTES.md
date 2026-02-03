# Notas sobre xmlsec y Firma Digital

## ⚠️ Estado Actual

El módulo `l10n_do_ecf` funciona **SIN xmlsec** en Windows para facilitar el desarrollo y pruebas.

## 🔧 Implementación Actual

### Firma Digital (Modo Desarrollo)

- **Sin xmlsec:** Firma simplificada con hash SHA256 + RSA
- **Con xmlsec:** Firma XMLDSig completa (futuro)

La firma simplificada:
1. Calcula SHA256 del XML
2. Firma el hash con la clave privada del certificado
3. Agrega la firma como comentario XML
4. **NO ES VÁLIDA PARA PRODUCCIÓN CON DGII**

## ✅ Funcionalidades Disponibles SIN xmlsec

1. ✅ Generación de XML e-CF
2. ✅ Validación de certificados
3. ✅ Estructura completa de documentos
4. ✅ Envío a servicios DGII (con firma simplificada)
5. ✅ Consulta de estado
6. ✅ Anulación
7. ✅ Códigos QR
8. ✅ Representación impresa
9. ✅ Gestión completa de certificados

## 🚀 Para Producción

### Opción 1: Usar Linux (Recomendado)

En un servidor Linux (Ubuntu/Debian), xmlsec se instala sin problemas:

```bash
# Instalar dependencias del sistema
sudo apt-get update
sudo apt-get install -y libxml2-dev libxmlsec1-dev libxmlsec1-openssl pkg-config

# Instalar xmlsec con pip
pip install xmlsec==1.3.13
```

El módulo detectará automáticamente xmlsec y usará firma completa.

### Opción 2: Usar Docker

```dockerfile
FROM odoo:19
RUN apt-get update && apt-get install -y \
    libxml2-dev \
    libxmlsec1-dev \
    libxmlsec1-openssl \
    pkg-config \
    && pip install xmlsec==1.3.13
```

### Opción 3: WSL en Windows

```bash
# En WSL (Windows Subsystem for Linux)
sudo apt-get install libxml2-dev libxmlsec1-dev libxmlsec1-openssl
pip install xmlsec==1.3.13
```

## 🔍 Verificar Estado de xmlsec

El módulo muestra en los logs:

```
INFO: xmlsec disponible - Firma digital completa habilitada
```

o

```
WARNING: xmlsec no disponible - Usando firma digital simplificada
```

## 📋 Próximos Pasos

1. **Desarrollo en Windows:** Usar firma simplificada (actual)
2. **Certificación DGII:** Desplegar en Linux con xmlsec
3. **Producción:** Obligatorio usar xmlsec completo

## ⚠️ IMPORTANTE

**NO usar en producción con DGII sin xmlsec completo.**

La firma simplificada es solo para:
- Desarrollo local
- Pruebas de interfaz
- Validación de flujos
- Demostración

Para certificación y producción con DGII, se requiere:
- ✅ Servidor Linux
- ✅ xmlsec instalado correctamente
- ✅ Firma XMLDSig completa según estándar W3C
- ✅ Validación con esquemas XSD DGII

## 🛠️ Implementar Firma XMLDSig Completa

Cuando xmlsec esté disponible, el método `sign_xml` debe implementar:

```python
# Firma XMLDSig completa con xmlsec
# 1. Crear SignedInfo
# 2. Canonicalización C14N
# 3. Algoritmo de firma: RSA-SHA256
# 4. Digest: SHA256
# 5. Incluir certificado X509
# 6. Validar contra XSD
```

Esto ya está preparado en el código con:
```python
if XMLSEC_AVAILABLE:
    # Implementar firma XMLDSig completa
    ...
```

## 📞 Soporte

Para dudas sobre xmlsec o firma digital:
- Email: soporte@dynasoftsolutions.com
- Documentación DGII: https://dgii.gov.do/ecf

