# 📝 Instrucciones para Completar el Cambio de Nombre del Módulo

## ✅ Cambios Ya Realizados

Los siguientes archivos ya han sido actualizados con el nuevo nombre **l10n_do_ext**:

1. ✅ `__manifest__.py` - Actualizado nombre, resumen y dependencias
2. ✅ `README.md` - Actualizada toda la documentación
3. ✅ `static/description/index.html` - Actualizada página de descripción
4. ✅ `static/description/banner.svg` - Nuevo banner con "Contabilidad Extendida"
5. ✅ `static/description/icon.svg` - Nuevo icono con badge "EXT" y símbolo "+"

## ⚠️ Pasos Pendientes a Realizar Manualmente

### Paso 1: Renombrar la Carpeta del Módulo

**IMPORTANTE**: Debe renombrar físicamente la carpeta del módulo:

```
ANTES: C:\odoo-19-addons\custom\l10n_do\
DESPUÉS: C:\odoo-19-addons\custom\l10n_do_ext\
```

**Cómo hacerlo:**
1. Cierre Odoo si está ejecutándose
2. En el Explorador de Archivos, navegue a: `C:\odoo-19-addons\custom\`
3. Renombre la carpeta `l10n_do` a `l10n_do_ext`

### Paso 2: Actualizar Odoo

Después de renombrar la carpeta:

1. **Inicie Odoo**
2. **Actualice la lista de aplicaciones**:
   - Vaya a **Apps**
   - Haga clic en el menú (☰) en la barra de búsqueda
   - Seleccione **"Actualizar Lista de Aplicaciones"**
   - Confirme la actualización

### Paso 3: Verificar la Instalación

1. En **Apps**, busque: `l10n_do_ext` o `República Dominicana - Contabilidad Extendida`
2. Debería ver el módulo con el nuevo nombre y los nuevos iconos
3. Si ya tenía instalado el módulo anterior (`l10n_do` personalizado):
   - **Desinstálelo primero**
   - Luego instale el nuevo `l10n_do_ext`

## 📋 Verificación de Conflictos

### Verificar que l10n_do Base Está Instalado

Este módulo **REQUIERE** el módulo oficial `l10n_do` de Odoo. Para verificar:

1. Vaya a **Apps**
2. Busque: `República Dominicana - Accounting` o `l10n_do`
3. Si no está instalado, **instálelo PRIMERO**
4. Luego instale `l10n_do_ext`

### Posibles Conflictos de IDs XML

El módulo actualmente define su propio chart template con IDs que comienzan con `l10n_do_`. 
Si experimenta conflictos con el módulo base, puede:

**Opción A: Uso Complementario**
- Use `l10n_do` (base) para el chart of accounts básico
- Use `l10n_do_ext` para reportes DGII, e-CF, y funcionalidades avanzadas
- Mantenga ambos módulos instalados

**Opción B: Modificar IDs XML (Avanzado)**
- Renombrar todos los IDs en los archivos XML de `data/` 
- Cambiar prefijo `l10n_do_` por `l10n_do_ext_`
- Esto requiere edición manual de ~100+ registros

## 🎯 Resumen de Funcionalidades del Módulo

El módulo **l10n_do_ext** extiende **l10n_do** con:

### ✨ Características Adicionales:
- ✅ **Reportes DGII 606 y 607** con exportación TXT
- ✅ **Integración e-CF** (Facturación Electrónica)
- ✅ **Códigos QR automáticos** en facturas
- ✅ **Wizards avanzados** para reportes y configuración
- ✅ **Gestión avanzada de NCF** con estados y validaciones
- ✅ **Plan contable extendido** de 8 dígitos (DGII + NIIF)
- ✅ **Grupos fiscales especializados** (Telecomunicaciones, Construcción, etc.)
- ✅ **8 Posiciones fiscales** para automatización de impuestos

### 📦 Dependencias Requeridas:
- Odoo 19.0 Community o Enterprise
- Módulo `l10n_do` (oficial de Odoo) - **OBLIGATORIO**
- Módulo `account`
- Módulo `account_edi`
- Módulo `l10n_latam_base`
- Python: `qrcode` (opcional para QR codes)

## 🆘 Solución de Problemas

### Error: "Módulo l10n_do no encontrado"
**Solución**: Instale primero el módulo oficial `l10n_do` desde Apps.

### Error: "Registro XML duplicado"
**Solución**: Verifique que no tiene instalado otro módulo personalizado `l10n_do`. 
Desinstale cualquier versión personalizada antigua antes de instalar `l10n_do_ext`.

### El módulo no aparece en Apps
**Solución**: 
1. Verifique que la carpeta se llame exactamente `l10n_do_ext`
2. Actualice la lista de aplicaciones en Odoo
3. Busque por "República Dominicana" o "l10n_do_ext"

### Error de permisos o modelos no encontrados
**Solución**: Reinicie Odoo con el comando de actualización:
```bash
odoo-bin -u l10n_do_ext -d nombre_base_datos
```

## ✅ Checklist Final

- [ ] Carpeta renombrada de `l10n_do` a `l10n_do_ext`
- [ ] Odoo reiniciado
- [ ] Lista de aplicaciones actualizada
- [ ] Módulo base `l10n_do` instalado
- [ ] Módulo `l10n_do_ext` visible en Apps
- [ ] Módulo `l10n_do_ext` instalado correctamente
- [ ] Reportes DGII funcionando
- [ ] Códigos QR generándose en facturas
- [ ] Sin errores en el log de Odoo

## 📞 Próximos Pasos

Después de completar el cambio de nombre:

1. **Configure su empresa** con la información fiscal de RD
2. **Configure las secuencias NCF** autorizadas por la DGII
3. **Configure e-CF** si cuenta con certificado digital
4. **Pruebe con facturas de prueba** antes de usar en producción
5. **Genere reportes DGII 606/607** para verificar funcionamiento

---

**Fecha de actualización**: Octubre 2025  
**Versión del módulo**: 19.0.1.0.0  
**Compatible con**: Odoo 19 Community y Enterprise

