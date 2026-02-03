# 🔍 GUÍA DE VERIFICACIÓN - l10n_do_ecf

## ¿El módulo está instalado?

### Método 1: Verificar en Apps
1. Odoo → Apps
2. Quitar filtro "Apps" 
3. Buscar: `l10n_do_ecf`
4. Verificar estado: ¿INSTALADO o Instalar?

### Método 2: Verificar en modo desarrollador
1. Activar modo desarrollador:
   - Ajustes → Scroll abajo → "Activar modo desarrollador"
2. Apps → Buscar módulo
3. Ver detalles técnicos

## ¿Los menús existen?

### Verificar en interfaz:
1. Contabilidad → Menú lateral izquierdo
2. Buscar: "Facturación Electrónica"

### Si NO aparece:
1. ¿Tienes permisos de administrador?
2. ¿El usuario tiene el grupo "Usuario e-CF"?

## Comandos de Verificación SQL (Opcional)

Si tienes acceso a la base de datos, ejecuta:

```sql
-- Verificar si el módulo está en la BD
SELECT name, state FROM ir_module_module WHERE name = 'l10n_do_ecf';

-- Verificar menús creados
SELECT id, name, parent_id FROM ir_ui_menu WHERE name LIKE '%Facturaci%Electr%';

-- Verificar modelos creados
SELECT model FROM ir_model WHERE model LIKE 'ecf%';

-- Verificar grupos
SELECT name FROM res_groups WHERE name LIKE '%ecf%';
```

## Soluciones Comunes

### Problema: Módulo no aparece en Apps
**Solución:**
1. Actualizar lista de apps
2. Verificar que el módulo esté en la ruta correcta
3. Reiniciar servidor Odoo

### Problema: Módulo instalado pero sin menús
**Solución:**
1. Actualizar módulo (Apps → l10n_do_ecf → Actualizar)
2. Verificar permisos del usuario
3. Limpiar caché del navegador

### Problema: Errores de instalación
**Solución:**
1. Ver logs de Odoo
2. Verificar dependencias
3. Reinstalar módulo

## Contacto
Si nada funciona, proporciona:
1. Screenshot de Apps mostrando el módulo
2. Screenshot del menú de Contabilidad
3. Logs de Odoo (si hay errores)

