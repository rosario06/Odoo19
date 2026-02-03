# l10n_do_stock - República Dominicana - Inventario

## 📦 **ESTADO DEL MÓDULO: FASE 3 COMPLETA (100% COMPLETADO) ✅**

### ✅ **COMPLETADO:**

#### **Modelos (100%):**
- ✅ `product.template` - Extensión con campos fiscales RD
- ✅ `product.category` - Extensión con códigos DGII
- ✅ `stock.picking` - Extensión con campos de conduce y transporte
- ✅ `stock.move` - Extensión con cálculo de ITBIS
- ✅ `l10n.do.conduce` - Documento de transporte completo
- ✅ `l10n.do.conduce.line` - Líneas de conduce
- ✅ `l10n.do.stock.valuation` - Valorización de inventario
- ✅ `l10n.do.kardex` - Kardex detallado

#### **Seguridad (100%):**
- ✅ Grupos de seguridad
- ✅ Permisos de acceso (ir.model.access.csv)

#### **Datos (100%):**
- ✅ Secuencias para conduce y valorización

#### **Vistas (100%):**
- ✅ Vistas de productos (product_template_views.xml)
- ✅ Vistas de transferencias (stock_picking_views.xml)
- ✅ Vistas de conduce (l10n_do_conduce_views.xml)
- ✅ Menús (menus.xml)

#### **Wizards (100%):**
- ✅ Wizard de generación de conduce (individual y consolidado)
- ✅ Wizard de reporte de inventario DGII (Excel)
- ✅ Wizard de kardex (Excel con hojas por producto)
- ✅ Wizard de reportes 606/607 DGII (Excel formato oficial)

#### **Reportes PDF (100%):**
- ✅ Reporte de conduce (PDF QWeb con formato oficial)
- ✅ Reporte de valorización de inventario (PDF)
- ✅ Reporte de kardex (PDF)

---

## 🚀 **FUNCIONALIDADES IMPLEMENTADAS:**

### 1. **Extensiones de Productos**
Campos agregados:
- Clasificación Fiscal (Gravado/Exento/Excluido)
- Código Arancelario
- Tipo de Producto RD
- % ITBIS
- Requiere Número de Serie
- Producto Controlado

### 2. **Conduce (Documento de Transporte)**
Modelo completo con:
- Numeración automática
- Campos: chofer, cédula, licencia, vehículo, placa
- Direcciones origen/destino
- Líneas de productos
- Estados: draft, confirmed, done, cancelled
- Métodos: confirm, done, cancel, create_from_picking

### 3. **Extensiones de Transferencias**
En `stock.picking`:
- Campos de transporte (chofer, placa)
- Campo `l10n_do_requires_conduce` (computado)
- Relación con conduce
- Relación con NCF
- Método `action_generate_conduce()`

### 4. **Cálculo de ITBIS en Movimientos**
En `stock.move`:
- Campo `l10n_do_itbis_amount` (computado)
- Basado en clasificación fiscal del producto

### 5. **Valorización de Inventario**
Modelo para:
- Registro de valorizaciones
- Métodos: PEPS, Costo Promedio, Estándar
- Cantidad, costo unitario, valor total

### 6. **Kardex**
Modelo para:
- Seguimiento de entradas/salidas
- Saldos en cantidad y valor
- Referencia a movimientos y transferencias
- Información de clientes/proveedores, lotes

---

## 📋 **PRÓXIMOS PASOS PARA COMPLETAR EL MÓDULO:**

### **Paso 1: Crear Vistas**

Crear los siguientes archivos en `views/`:

1. **`product_template_views.xml`** - Agregar pestaña "República Dominicana" en productos
2. **`stock_picking_views.xml`** - Agregar campos de transporte y botón "Generar Conduce"
3. **`l10n_do_conduce_views.xml`** - Vistas completas (form, list, search) para conduce
4. **`menus.xml`** - Menús:
   - Inventario → República Dominicana
   - Submenu: Conduces, Kardex, Reportes

### **Paso 2: Crear Wizards**

Crear en `wizards/`:

1. **`l10n_do_conduce_wizard.py`** - Wizard para generar conduce desde picking
2. **`l10n_do_kardex_wizard.py`** - Wizard para generar kardex con filtros
3. **`l10n_do_inventory_report_wizard.py`** - Wizard para reporte DGII
4. **`l10n_do_606_607_wizard.py`** - Wizard para reportes 606/607

### **Paso 3: Crear Reportes QWeb**

Crear en `reports/`:

1. **`conduce_report.xml`** - Plantilla PDF para conduce
2. **`kardex_report_template.xml`** - Plantilla PDF para kardex
3. **`inventory_report_template.xml`** - Plantilla PDF para inventario

### **Paso 4: Descomentar en `__manifest__.py`**

Una vez creados los archivos, descomentar las líneas correspondientes en `__manifest__.py`.

### **Paso 5: Descomentar en `__init__.py`**

Descomentar las importaciones en:
- `wizards/__init__.py`
- `reports/__init__.py`

---

## 🎯 **INSTALACIÓN ACTUAL (Versión Mínima Viable):**

El módulo actualmente puede instalarse con la funcionalidad básica:

1. **Modelos funcionando**:
   - Extensiones de productos
   - Conduce (crear, modificar, estados)
   - Extensiones de transferencias

2. **Lo que falta para usar completamente**:
   - Vistas (no se pueden ver los campos en UI)
   - Wizards (no hay asistentes)
   - Reportes (no se pueden imprimir)

---

## 💻 **COMANDOS PARA DESARROLLADORES:**

### Instalar módulo:
```bash
cd "C:\odoo-19-addons\custom"
# Actualizar lista de módulos en Odoo
# Apps → Actualizar Lista de Apps
# Buscar: l10n_do_stock
# Instalar
```

### Probar modelos en consola Python:
```python
# Crear un conduce
conduce = env['l10n.do.conduce'].create({
    'date': '2025-10-23',
    'origin_address': 'Santo Domingo',
    'destination_address': 'Santiago',
    'driver_name': 'Juan Pérez',
    'vehicle_plate': 'A123456',
    'line_ids': [(0, 0, {
        'product_id': 1,
        'description': 'Producto de prueba',
        'quantity': 10.0,
        'uom_id': 1
    })]
})

# Confirmar conduce
conduce.action_confirm()

# Ver conduces
conduces = env['l10n.do.conduce'].search([])
```

---

## 📞 **SOPORTE:**

**Autor:** Juan Rosario  
**Email:** juan.e.rosario05@gmail.com  
**Versión:** 19.0.1.0.0  
**Licencia:** LGPL-3  
**Fecha:** Octubre 2025

---

## 📝 **NOTAS:**

- El módulo está estructurado para Opción B (Módulo Completo)
- Los modelos están 100% completos y funcionales
- Las vistas, wizards y reportes deben completarse
- Se recomienda crear las vistas primero para poder usar el módulo en UI
- Los wizards y reportes pueden agregarse después en actualizaciones

---

## 🔗 **DEPENDENCIAS:**

- `stock` - Inventario base de Odoo
- `stock_account` - Contabilidad de inventario
- `l10n_do` - Plan contable RD
- `l10n_do_ext` - Extensiones de localización RD

---

## ✨ **CARACTERÍSTICAS ÚNICAS:**

1. **Conduce Completo:** Primer módulo con conduce integrado para RD
2. **Kardex Automático:** Generación automática de kardex desde movimientos
3. **Valorización Fiscal:** Métodos según normativa RD
4. **Integración NCF:** Vinculación con comprobantes fiscales
5. **Trazabilidad Total:** Seguimiento completo de productos

