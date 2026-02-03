# 🧪 GUÍA DE PRUEBAS - l10n_do_hr_payroll
## Módulo de Nómina República Dominicana para Odoo 19

**Versión**: 19.0.1.0.0  
**Fecha**: 23 de Octubre, 2025  
**Autor**: Juan Rosario

---

## 📋 PRE-REQUISITOS

### ✅ Módulos Instalados (REQUERIDOS)

Antes de instalar `l10n_do_hr_payroll`, verifica que estén instalados:

1. ✅ **hr** - Empleados (base Odoo)
2. ✅ **hr_payroll** - OCA Payroll Community
3. ✅ **hr_payroll_account** - OCA Payroll Accounting
4. ✅ **l10n_do** - Plan Contable República Dominicana
5. ✅ **l10n_do_ext** - Extensiones Localización RD

**Verificar en Odoo:**
```
Apps → Buscar cada módulo → Estado: "Instalado"
```

---

## 🚀 FASE 1: INSTALACIÓN DEL MÓDULO

### Paso 1.1: Actualizar Lista de Apps

1. Ir a: `Apps` (Aplicaciones)
2. Clic en: `⋮` (menú) → `Actualizar Lista de Apps`
3. Confirmar actualización

### Paso 1.2: Buscar el Módulo

1. En el buscador de Apps, escribir: `República Dominicana - Nómina`
2. Debería aparecer el módulo con descripción:
   - **Nombre**: República Dominicana - Nómina
   - **Categoría**: Localization
   - **Versión**: 19.0.1.0.0
   - **Autor**: Juan Rosario

### Paso 1.3: Instalar

1. Clic en el botón `Instalar`
2. Esperar a que termine la instalación (puede tardar 1-2 minutos)
3. Si hay errores, **copiar el mensaje de error completo**

### ✅ Verificación de Instalación

**ÉXITO si se cumplen estos puntos:**

1. ✅ El módulo aparece con estado `Instalado`
2. ✅ No hay errores en el log de Odoo
3. ✅ El menú `Payroll` está visible en la barra superior

**Si hay ERRORES:**
- Copiar el mensaje de error completo
- Verificar que las dependencias estén instaladas
- Revisar el log de Odoo: `C:\Program Files\Odoo 19.0...\server\odoo.log`

---

## 🔧 FASE 2: VERIFICAR CONFIGURACIÓN

### Paso 2.1: Verificar Grupos de Seguridad

1. Ir a: `Configuración` → `Usuarios y Compañías` → `Grupos`
2. Buscar: "RD Payroll"
3. **Verificar que existan:**
   - ✅ RD Payroll User
   - ✅ RD Payroll Manager

### Paso 2.2: Asignar Permisos al Usuario

1. Ir a: `Configuración` → `Usuarios y Compañías` → `Usuarios`
2. Seleccionar tu usuario (ej: Admin)
3. En la pestaña `Permisos de Acceso`:
   - ✅ Marcar: **RD Payroll Manager**
   - ✅ Marcar: **Payroll Manager** (si no está)
   - ✅ Marcar: **HR Manager** (si no está)
4. Guardar

### Paso 2.3: Verificar Datos Iniciales

#### 2.3.1 Tasas TSS
1. Ir a: `Payroll` → `Configuración` → `Configuración RD` → `Tasas TSS`
2. **Debe existir un registro:**
   - ✅ Nombre: "Tasas TSS 2024-2025"
   - ✅ AFP Empleado: 2.87%
   - ✅ AFP Empleador: 7.10%
   - ✅ Estado: Activo

#### 2.3.2 Tramos ISR
1. Ir a: `Payroll` → `Configuración` → `Configuración RD` → `Tramos ISR`
2. **Deben existir 4 registros:**
   - ✅ Tramo 1: 0 - 416,220 @ 0%
   - ✅ Tramo 2: 416,220 - 624,329 @ 15%
   - ✅ Tramo 3: 624,329 - 867,123 @ 20%
   - ✅ Tramo 4: 867,123+ @ 25%

#### 2.3.3 Salarios Mínimos
1. Ir a: `Payroll` → `Configuración` → `Configuración RD` → `Salarios Mínimos`
2. **Debe existir un registro:**
   - ✅ Nombre: "Salarios Mínimos 2024-2025"
   - ✅ Sector Privado Grande: 27,000.00
   - ✅ Estado: Activo

### Paso 2.4: Verificar Estructura Salarial

1. Ir a: `Payroll` → `Configuración` → `Structures`
2. Buscar: "Nómina República Dominicana"
3. Abrir el registro
4. **Verificar que tenga 16 reglas:**

| # | Regla | Código | Categoría |
|---|-------|--------|-----------|
| 1 | Salario Básico | BASIC | BASIC |
| 2 | Salario Bruto | GROSS | GROSS |
| 3 | AFP Empleado | AFP_EMPLOYEE | TSS_EMP |
| 4 | ARS Empleado | ARS_EMPLOYEE | TSS_EMP |
| 5 | SFS Empleado | SFS_EMPLOYEE | TSS_EMP |
| 6 | AFP Empleador | AFP_EMPLOYER | TSS_EMPR |
| 7 | ARS Empleador | ARS_EMPLOYER | TSS_EMPR |
| 8 | SFS Empleador | SFS_EMPLOYER | TSS_EMPR |
| 9 | Infotep | INFOTEP | TSS_EMPR |
| 10 | Neto a Pagar | NET | NET |
| 11 | Provisión Cesantía | PROVISION_CESANTIA | PROV |
| 12 | Provisión Preaviso | PROVISION_PREAVISO | PROV |
| 13 | Provisión Vacaciones | PROVISION_VACACIONES | PROV |
| 14 | Provisión Salario Navidad | PROVISION_SALARIO_NAVIDAD | PROV |
| 15 | Total Provisiones | TOTAL_PROVISIONS | PROV |
| 16 | Costo Total Empleador | TOTAL_COST | COST |

---

## 👤 FASE 3: CREAR DATOS DE PRUEBA

### Paso 3.1: Crear Empleado de Prueba

1. Ir a: `HR` → `Empleados` → `Crear`
2. Completar:
   ```
   Nombre: Juan Pérez Rodríguez
   Cédula: 001-1234567-8
   Número TSS: 12345678901
   Email: juan.perez@test.com
   ```
3. Guardar

### Paso 3.2: Crear Contrato

1. En el formulario del empleado, ir a pestaña `Contratos`
2. Clic en `Crear`
3. Completar:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFORMACIÓN BÁSICA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Referencia del Contrato: CONT-001-2025
Empleado: Juan Pérez Rodríguez
Fecha de Inicio: 01/01/2025
Salario: 30,000.00
Estado: Running (Abierto)
Estructura Salarial: Nómina República Dominicana ⭐

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFORMACIÓN TSS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Número AFP: AFP-12345678
Número ARS: ARS-12345678
ARS Proveedor: SENASA
Tipo SFS: Plan Estatal (SENASA)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SALARIO MÍNIMO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Sector Salario Mínimo: Sector Privado - Grandes Empresas

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ISR:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Dependientes para ISR: 2
Otras Deducciones ISR: 0.00

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRESTACIONES LABORALES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Calcular Provisiones: SÍ (marcar checkbox)
Días de Vacaciones/Año: 14
```

4. Guardar

---

## 💰 FASE 4: GENERAR NÓMINA DE PRUEBA

### Paso 4.1: Crear Payslip

1. Ir a: `Payroll` → `Employee Payslips`
2. Clic en `Crear`
3. Completar:
   ```
   Empleado: Juan Pérez Rodríguez
   Período: Mes actual
   Fecha Desde: 01/MM/YYYY
   Fecha Hasta: 30/MM/YYYY
   ```
4. Guardar

### Paso 4.2: Computar Nómina

1. En el payslip, clic en botón: `Compute Sheet` (Calcular Hoja)
2. Esperar a que se completen los cálculos

### Paso 4.3: Verificar Cálculos (CRUCIAL) ✅

#### **SALARIO BASE: RD$ 30,000**

**A. DEDUCCIONES EMPLEADO (TSS):**

| Concepto | Fórmula | Valor Esperado | ✓ |
|----------|---------|----------------|---|
| AFP Empleado | 30,000 × 2.87% | -861.00 | ☐ |
| ARS Empleado | 30,000 × 3.04% | -912.00 | ☐ |
| SFS Empleado | 30,000 × 3.04% | -912.00 | ☐ |
| **TOTAL TSS Empleado** | | **-2,685.00** | ☐ |

**B. NETO A PAGAR:**

| Concepto | Cálculo | Valor Esperado | ✓ |
|----------|---------|----------------|---|
| Salario Bruto | 30,000.00 | 30,000.00 | ☐ |
| TSS Empleado | | -2,685.00 | ☐ |
| **NETO A PAGAR** | | **27,315.00** | ☐ |

**C. APORTES PATRONALES (TSS):**

| Concepto | Fórmula | Valor Esperado | ✓ |
|----------|---------|----------------|---|
| AFP Empleador | 30,000 × 7.10% | 2,130.00 | ☐ |
| ARS Empleador | 30,000 × 7.09% | 2,127.00 | ☐ |
| SFS Empleador | 30,000 × 7.09% | 2,127.00 | ☐ |
| Infotep | 30,000 × 1.00% | 300.00 | ☐ |
| **TOTAL TSS Empleador** | | **6,684.00** | ☐ |

**D. PROVISIONES LABORALES:**

| Concepto | Fórmula | Valor Esperado | ✓ |
|----------|---------|----------------|---|
| Cesantía | 30,000 × 8.33% | 2,499.00 | ☐ |
| Preaviso | 30,000 × 8.33% | 2,499.00 | ☐ |
| Vacaciones | (30,000/30)×(14/12) | 1,166.67 | ☐ |
| Salario Navidad | 30,000 × 8.33% | 2,499.00 | ☐ |
| **TOTAL Provisiones** | | **8,663.67** | ☐ |

**E. COSTO TOTAL:**

| Concepto | Cálculo | Valor Esperado | ✓ |
|----------|---------|----------------|---|
| Salario Base | 30,000.00 | 30,000.00 | ☐ |
| TSS Empleador | | 6,684.00 | ☐ |
| Provisiones | | 8,663.67 | ☐ |
| **COSTO TOTAL** | | **45,347.67** | ☐ |

### ✅ CRITERIOS DE ÉXITO:

- ☐ Todos los cálculos coinciden con valores esperados (±1 peso de diferencia por redondeo)
- ☐ Neto a pagar = **27,315.00**
- ☐ Costo total = **45,347.67**
- ☐ Porcentaje total: **151.16%** del salario base

---

## 📊 FASE 5: PROBAR REPORTES

### Paso 5.1: Generar Reporte TSS

1. Ir a: `Payroll` → `Reportes RD` → `Generar Reporte TSS`
2. Completar:
   ```
   Desde: 01/MM/YYYY
   Hasta: 30/MM/YYYY
   Tipo de Reporte: Excel
   ```
3. Clic en: `Generar Reporte`
4. Clic en: `Descargar Excel`

**✅ Verificar:**
- ☐ Se descarga archivo Excel
- ☐ Contiene datos del empleado Juan Pérez
- ☐ Totales coinciden con el payslip

### Paso 5.2: Generar IT-1

1. Ir a: `Payroll` → `Reportes RD` → `Generar IT-1 (DGII)`
2. Completar:
   ```
   Año Fiscal: 2025
   Formato: Excel (IT-1)
   ```
3. Clic en: `Generar IT-1`
4. Clic en: `Descargar`

**✅ Verificar:**
- ☐ Se descarga archivo Excel
- ☐ Formato IT-1 correcto
- ☐ Contiene datos del empleado

### Paso 5.3: Ver Aportes TSS

1. Ir a: `Payroll` → `Reportes RD` → `Aportes TSS`
2. **Verificar:**
   - ☐ Se ve listado de aportes
   - ☐ Filtros funcionan (por período, empleado, estado)
   - ☐ Totales se calculan correctamente

### Paso 5.4: Ver Retenciones ISR

1. Ir a: `Payroll` → `Reportes RD` → `Retenciones ISR`
2. **Verificar:**
   - ☐ Se ve listado de retenciones
   - ☐ Cálculo de ISR es correcto
   - ☐ Tasa efectiva se muestra

---

## 🎯 FASE 6: PRUEBAS ADICIONALES

### Prueba 6.1: Desactivar Provisiones

1. Abrir contrato de Juan Pérez
2. Desmarcar: `Calcular Provisiones`
3. Guardar
4. Crear nuevo payslip
5. **Verificar:**
   - ☐ Provisiones = 0.00
   - ☐ Costo Total = Salario + TSS Empleador

### Prueba 6.2: Cambiar Días de Vacaciones

1. Abrir contrato de Juan Pérez
2. Cambiar: `Días de Vacaciones/Año` = 21
3. Guardar
4. Crear nuevo payslip
5. **Verificar:**
   - ☐ Provisión Vacaciones aumenta
   - ☐ Nuevo valor: (30,000/30) × (21/12) = 1,750.00

### Prueba 6.3: Empleado con Salario Mayor

Crear empleado con salario de RD$ 50,000 y verificar:
- ☐ TSS se calcula correctamente
- ☐ ISR se aplica (si supera tramo exento)
- ☐ Provisiones son proporcionales

---

## ❌ ERRORES COMUNES Y SOLUCIONES

### Error 1: "Module not found"
**Causa:** Dependencias no instaladas  
**Solución:** Instalar hr_payroll y hr_payroll_account de OCA

### Error 2: "Field does not exist"
**Causa:** Migración incompleta  
**Solución:** Actualizar módulo hr_payroll a versión 19.0

### Error 3: Provisiones no aparecen
**Causa:** Campo `provision_enabled` no marcado  
**Solución:** En contrato, marcar checkbox "Calcular Provisiones"

### Error 4: Cálculos incorrectos
**Causa:** Tasas TSS mal configuradas  
**Solución:** Verificar datos en `Tasas TSS` están activos y con fechas correctas

### Error 5: No aparece menú "Payroll"
**Causa:** Permisos no asignados  
**Solución:** Asignar grupos "RD Payroll Manager" y "Payroll Manager" al usuario

---

## 📝 CHECKLIST FINAL DE PRUEBAS

### ✅ INSTALACIÓN
- ☐ Módulo instalado sin errores
- ☐ Grupos de seguridad creados
- ☐ Datos iniciales cargados
- ☐ Menús visibles

### ✅ CONFIGURACIÓN
- ☐ Tasas TSS configuradas
- ☐ Tramos ISR configurados
- ☐ Salarios mínimos configurados
- ☐ Estructura salarial con 16 reglas

### ✅ DATOS DE PRUEBA
- ☐ Empleado creado
- ☐ Contrato creado con todos los campos
- ☐ Estructura salarial asignada

### ✅ CÁLCULO DE NÓMINA
- ☐ Payslip genera correctamente
- ☐ TSS Empleado calculado: -2,685.00
- ☐ Neto a pagar: 27,315.00
- ☐ TSS Empleador: 6,684.00
- ☐ Provisiones: 8,663.67
- ☐ Costo Total: 45,347.67

### ✅ REPORTES
- ☐ Reporte TSS genera Excel
- ☐ IT-1 genera Excel
- ☐ Aportes TSS visibles
- ☐ Retenciones ISR visibles

### ✅ FUNCIONALIDADES AVANZADAS
- ☐ Provisiones on/off funciona
- ☐ Días vacaciones configurable
- ☐ Múltiples empleados funcionan

---

## 🎉 RESULTADO FINAL

### ✅ SI TODOS LOS CHECKS ESTÁN MARCADOS:

**🎊 ¡FELICIDADES! EL MÓDULO ESTÁ 100% FUNCIONAL**

El módulo `l10n_do_hr_payroll` está listo para:
- ✅ Usar en PRODUCCIÓN
- ✅ Desplegar a CLIENTES
- ✅ Calcular nóminas REALES
- ✅ Generar reportes OFICIALES (TSS, DGII)

### ⚠️ SI HAY ERRORES:

1. Documentar el error exacto
2. Copiar mensaje de error completo
3. Verificar que se siguieron todos los pasos
4. Contactar soporte si persiste

---

## 📞 SOPORTE

**Desarrollador:** Juan Rosario  
**Email:** juan.e.rosario05@gmail.com  
**Módulo:** l10n_do_hr_payroll v19.0.1.0.0  
**Fecha:** Octubre 2025

---

## 📊 RESUMEN EJECUTIVO

**Módulo de Nómina República Dominicana para Odoo 19**

**Incluye:**
- ✅ TSS (AFP, ARS, SFS, Infotep)
- ✅ ISR (Impuesto Sobre la Renta)
- ✅ Prestaciones Laborales (Cesantía, Preaviso, Vacaciones, Navidad)
- ✅ Reportes TSS y IT-1 (DGII)
- ✅ Tasas dinámicas configurables
- ✅ Histórico completo

**Cumple con:**
- ✅ Código de Trabajo de RD
- ✅ Ley 87-01 (TSS)
- ✅ DGII (IT-1)
- ✅ Reportes obligatorios

**Estado:** ✅ **PRODUCTION READY**

---

**Fin de la Guía de Pruebas**

