# ✅ GUÍA DE VERIFICACIÓN - l10n_do_ecf

## 📋 Checklist de Verificación

### 1. Verificar Instalación del Módulo

**Ubicación:** Apps → Buscar "l10n_do_ecf"

- [ ] El módulo aparece como "INSTALADO"
- [ ] La versión es 19.0.1.0.0
- [ ] La descripción se muestra correctamente con el HTML

---

### 2. Verificar Menús en Contabilidad

**Ubicación:** Contabilidad (menú principal)

- [ ] Existe menú "Facturación Electrónica"
- [ ] Submenú "Documentos e-CF" visible
- [ ] Submenú "Certificados Digitales" visible
- [ ] Submenú "Configuración" visible

---

### 3. Verificar Modelos (Base de Datos)

**Desde Ajustes Técnicos:**

1. Ve a: **Ajustes** (Settings)
2. Activa **Modo Desarrollador**:
   - Scroll al final de la página
   - Clic en "Activar el modo de desarrollador"
3. Ve a: **Ajustes Técnicos → Estructura de la Base de Datos → Modelos**
4. Busca los siguientes modelos:

- [ ] `ecf.document` - Documentos e-CF
- [ ] `ecf.certificate` - Certificados Digitales  
- [ ] `ecf.document.log` - Historial de documentos
- [ ] `ecf.send.wizard` - Asistente de envío
- [ ] `ecf.test.connection.wizard` - Prueba de conexión
- [ ] `ecf.cancel.wizard` - Asistente de anulación

---

### 4. Verificar Vistas

**Desde Ajustes Técnicos:**

1. Ve a: **Ajustes Técnicos → Interfaz de usuario → Vistas**
2. Busca vistas del módulo `l10n_do_ecf`:

#### Documentos e-CF:
- [ ] `ecf.document.form` - Vista de formulario
- [ ] `ecf.document.tree` - Vista de lista
- [ ] `ecf.document.search` - Vista de búsqueda (simplificada)

#### Certificados:
- [ ] `ecf.certificate.form` - Vista de formulario
- [ ] `ecf.certificate.tree` - Vista de lista
- [ ] `ecf.certificate.search` - Vista de búsqueda

---

### 5. Verificar Grupos de Seguridad

**Desde Ajustes Técnicos:**

1. Ve a: **Ajustes → Usuarios y Compañías → Grupos**
2. Busca:

- [ ] Grupo: "Usuario e-CF"
- [ ] Grupo: "Gerente e-CF"

**Asignar permisos a tu usuario:**
1. Ve a: **Ajustes → Usuarios y Compañías → Usuarios**
2. Selecciona tu usuario
3. En la pestaña "Control de Acceso"
4. Busca "Facturación Electrónica DGII"
5. Asigna el rol "Gerente e-CF"

---

### 6. Verificar Acceso a Documentos e-CF

**Prueba de acceso:**

1. Ve a: **Contabilidad → Facturación Electrónica → Documentos e-CF**
2. Verifica:
   - [ ] La página carga sin errores
   - [ ] Puedes ver el botón "Crear"
   - [ ] La vista de lista funciona
   - [ ] El filtro de búsqueda funciona

---

### 7. Verificar Acceso a Certificados

**Prueba de acceso:**

1. Ve a: **Contabilidad → Facturación Electrónica → Certificados Digitales**
2. Verifica:
   - [ ] La página carga sin errores
   - [ ] Puedes ver el botón "Crear"
   - [ ] La vista de lista funciona

---

### 8. Verificar Integración con Facturas

**Prueba de campos:**

1. Ve a: **Contabilidad → Clientes → Facturas**
2. Abre o crea una factura
3. Busca en el formulario:
   - [ ] Campos invisibles agregados (has_ecf, can_send_ecf, ecf_state, ecf_number)
   - [ ] Botones en header (pueden no aparecer si no hay datos aún)

---

### 9. Verificar Dependencias Python

**Desde terminal/consola de Odoo:**

Ejecuta este script Python en el shell de Odoo:

```python
# Verificar módulos Python instalados
import sys

modules_to_check = [
    'zeep',
    'lxml', 
    'cryptography',
    'qrcode',
    'requests',
    'xmlschema',
    'dateutil',
]

print("=== VERIFICACIÓN DE DEPENDENCIAS PYTHON ===\n")
for module in modules_to_check:
    try:
        __import__(module)
        print(f"✅ {module}: INSTALADO")
    except ImportError:
        print(f"❌ {module}: NO ENCONTRADO")

# Verificar xmlsec (opcional)
try:
    import xmlsec
    print(f"✅ xmlsec: INSTALADO (firma completa)")
except ImportError:
    print(f"⚠️  xmlsec: NO INSTALADO (firma simplificada en Windows)")
```

---

### 10. Verificar Archivos de Datos

**Desde Ajustes Técnicos:**

1. Ve a: **Ajustes Técnicos → Secuencias e Identificadores → Secuencias**
2. Busca secuencias con prefijo `ECF/`

---

## 🎯 RESULTADO ESPERADO

### ✅ Instalación Correcta:

- Módulo instalado en Apps
- Menús visibles en Contabilidad
- 6 modelos creados en base de datos
- Vistas cargando sin errores
- 2 grupos de seguridad creados
- Dependencias Python instaladas
- Acceso funcional a todas las secciones

### ⚠️ Si algo falla:

1. **Error de permisos:** Asigna el grupo "Gerente e-CF" a tu usuario
2. **Error 404 en menús:** Actualiza la lista de Apps y reinicia Odoo
3. **Vistas no cargan:** Verifica el modo desarrollador y revisa logs
4. **Dependencias faltantes:** Ejecuta `pip install -r requirements.txt`

---

## 🔧 COMANDOS ÚTILES

### Ver logs de Odoo:
```bash
# En la consola donde corre Odoo
# Buscar líneas con "l10n_do_ecf"
```

### Reinstalar el módulo (si es necesario):
```
1. Apps → Buscar "l10n_do_ecf"
2. Clic en el módulo
3. Clic en "Desinstalar"
4. Confirmar
5. Clic en "Instalar"
```

### Actualizar el módulo:
```
1. Apps → Buscar "l10n_do_ecf"
2. Clic en el módulo  
3. Clic en "Actualizar"
```

---

## 📊 ESTADO ACTUAL DEL MÓDULO

| Componente | Estado | Notas |
|------------|--------|-------|
| **Instalación** | ✅ Completa | Módulo instalado correctamente |
| **Modelos** | ✅ Funcionales | 6 modelos + wizards |
| **Vistas** | ⚠️ Simplificadas | Búsquedas básicas |
| **Seguridad** | ✅ Activa | 2 grupos funcionales |
| **Menús** | ✅ Visibles | 3 submenús activos |
| **Integración Facturas** | ⚠️ Básica | Campos agregados |
| **Dependencias** | ✅ Instaladas | zeep, lxml, crypto, qr |
| **Firma XML** | ⚠️ Condicional | Simplificada en Windows |

---

## 🚀 PRÓXIMOS PASOS

1. ✅ **Verificación completa** (esta guía)
2. ⏭️ **Configuración inicial** de empresa
3. ⏭️ **Prueba de certificado** (opcional en desarrollo)
4. ⏭️ **Refinamiento de vistas** avanzadas
5. ⏭️ **Implementación completa** de webservices DGII

---

**Fecha de verificación:** {{ FECHA }}  
**Versión módulo:** 19.0.1.0.0 (Beta)  
**Versión Odoo:** 19.0.20250927

