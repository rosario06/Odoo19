# l10n_do_account_asset - República Dominicana - Activos Fijos

## 📦 **ESTADO DEL MÓDULO: 100% COMPLETADO** ✅

### **Gestión Completa de Activos Fijos con Depreciación Automática según DGII**

---

## 🚀 **FUNCIONALIDADES PRINCIPALES:**

### **1. Gestión de Activos Fijos** 🏗️
- ✅ Registro completo de activos con toda la información
- ✅ 10 categorías predefinidas según tasas DGII
- ✅ Información fiscal completa (NCF, RNC proveedor)
- ✅ Ubicación física y responsable del activo
- ✅ Fotografías y documentos adjuntos
- ✅ Seguimiento de estado (Borrador → En Uso → Cerrado → Baja)

### **2. Depreciación Automática** 📉
- ✅ **Método Lineal** (principal)
- ✅ **Método Acelerado** (opcional)
- ✅ **Tasas DGII oficiales** predefinidas por categoría
- ✅ Generación automática de líneas de depreciación
- ✅ Asientos contables automáticos
- ✅ Cron job para depreciación mensual

### **3. Categorías según DGII** 📂
| Categoría | Tasa Anual | Vida Útil |
|-----------|------------|-----------|
| Edificios | 5% | 20 años |
| Vehículos | 25% | 4 años |
| Maquinaria | 15% | 6.67 años |
| Equipos Oficina | 20% | 5 años |
| Computadoras | 33.33% | 3 años |
| Herramientas | 25% | 4 años |
| Mobiliario | 10% | 10 años |
| Comunicación | 20% | 5 años |
| Instalaciones | 10% | 10 años |
| Mejoras Arrendadas | 20% | Variable |

### **4. Mantenimientos** 🔧
- ✅ Registro de mantenimientos (preventivos, correctivos, predictivos)
- ✅ Costos y proveedores
- ✅ Programación de próximo mantenimiento
- ✅ Historial completo
- ✅ Estados (Programado → En Progreso → Completado)

### **5. Bajas y Ventas** 📤
- ✅ Baja de activos (venta, desecho, donación, pérdida, robo)
- ✅ Cálculo automático de ganancia/pérdida
- ✅ Generación de asientos contables
- ✅ Vinculación con facturas de venta

### **6. Integración Contable** 💰
- ✅ Asientos automáticos de depreciación
- ✅ Cuentas contables configurables por categoría
- ✅ Diario de activos fijos
- ✅ Vinculación con NCF de compra

### **7. Integración con Facturas** 📄
- ✅ Botón "Crear Activo" en facturas de compra
- ✅ Configuración de productos como activos
- ✅ Vinculación automática con NCF

### **8. Reportes** 📊
- ✅ **Reporte Excel DGII** (formato oficial con todos los activos)
- ✅ **PDF Ficha de Activo** (información completa del activo)
- ✅ **PDF Tabla de Depreciación** (todas las líneas)
- ✅ Filtros por categoría, estado, fechas

### **9. Wizards** 🧙
- ✅ **Calcular Depreciación** (masiva por fecha)
- ✅ **Dar de Baja** (asistente completo)
- ✅ **Reporte DGII** (Excel formato oficial)
- ✅ **Importar desde Excel** (carga masiva)

---

## ⚖️ **CUMPLIMIENTO LEGAL:**

### **Normativas Aplicadas:**
- ✅ **Ley 11-92** (Código Tributario RD)
- ✅ **Norma 02-05** (Reglamento ISR - Tasas de Depreciación)
- ✅ **Norma General 06-2018** (NCF)
- ✅ **NIC 16** (Propiedad, Planta y Equipo)

---

## 📁 **ESTRUCTURA DEL MÓDULO:**

```
l10n_do_account_asset/
├── models/ (8 archivos)
│   ├── account_asset_category.py
│   ├── account_asset.py
│   ├── account_asset_depreciation.py
│   ├── account_asset_maintenance.py
│   ├── account_asset_disposal.py
│   ├── account_move.py
│   ├── res_company.py
│   └── product_template.py
├── views/ (6 archivos XML)
├── wizards/ (8 archivos: 4 Python + 4 XML)
├── reports/ (3 reportes PDF QWeb)
├── data/ (3 archivos: secuencias, categorías, cron)
├── security/ (2 archivos)
└── static/description/
```

---

## 🔧 **INSTALACIÓN:**

### **1. Dependencias Python:**
```bash
pip install xlsxwriter openpyxl
```

### **2. Dependencias Odoo:**
- `base`
- `account`
- `l10n_do`
- `l10n_latam_invoice_document`
- `product`

### **3. Instalación:**
```
Apps → Buscar "República Dominicana - Activos Fijos" → Instalar
```

---

## 📖 **USO BÁSICO:**

### **Caso 1: Registrar un Activo**
```
1. Contabilidad → Activos Fijos → Activos → Crear
2. Llenar datos:
   - Nombre: "Vehículo Toyota Corolla 2024"
   - Categoría: Vehículos (25%)
   - Valor: RD$ 1,500,000
   - Fecha: 01/01/2025
3. Guardar → Activar
4. Sistema genera líneas de depreciación automáticamente
```

### **Caso 2: Crear Activo desde Factura**
```
1. Contabilidad → Proveedores → Facturas → Crear
2. Llenar factura con NCF
3. Producto marcado como "Puede ser Activo"
4. Contabilizar factura
5. Botón "Crear Activo" → Se abre activo pre-llenado
```

### **Caso 3: Depreciación Mensual**
```
1. Contabilidad → Activos Fijos → Reportes → Calcular Depreciación
2. Fecha: 31/01/2025
3. Calcular
4. Sistema contabiliza todas las depreciaciones del mes
```

### **Caso 4: Reporte DGII**
```
1. Activos Fijos → Reportes → Reporte de Activos DGII
2. Período: 01/01/2024 - 31/12/2024
3. Generar → Descargar Excel
4. Excel con todos los activos en formato oficial
```

---

## 📊 **MÉTRICAS DEL MÓDULO:**

| Componente | Cantidad | Líneas Código |
|------------|----------|---------------|
| Modelos Python | 8 | ~1,800 |
| Vistas XML | 6 | ~900 |
| Wizards Python | 4 | ~600 |
| Wizards XML | 4 | ~300 |
| Reportes PDF | 3 | ~300 |
| Datos | 3 | ~150 |
| Seguridad | 2 | ~30 |
| **TOTAL** | **30** | **~4,080** |

---

## 🎯 **CARACTERÍSTICAS DESTACADAS:**

1. **🤖 Automatización Total:** Depreciación automática mensual via cron
2. **📊 Reportes DGII:** Excel formato oficial para auditorías
3. **💼 Integración Completa:** Facturas, NCF, Contabilidad
4. **🔧 Mantenimientos:** Gestión completa con costos
5. **📈 Dashboard:** Valores en tiempo real en cards
6. **🎨 Interfaz Moderna:** Vistas list, kanban, form profesionales
7. **📄 PDFs Profesionales:** Fichas y tablas de depreciación
8. **📥 Importación Excel:** Carga masiva de activos

---

## 📞 **INFORMACIÓN:**

**Desarrollador:** Juan Rosario  
**Email:** juan.e.rosario05@gmail.com  
**Versión:** 19.0.1.0.0  
**Licencia:** LGPL-3  
**Fecha:** Octubre 2025  
**Estado:** **PRODUCCIÓN READY** ✅

---

## 🎉 **¡MÓDULO 100% COMPLETO Y FUNCIONAL!**

Listo para usar en entornos de producción.

