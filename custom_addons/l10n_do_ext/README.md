# República Dominicana - Localización Extendida (l10n_do_ext)

![Versión](https://img.shields.io/badge/version-19.0.1.0.0-blue)
![Licencia](https://img.shields.io/badge/license-LGPL--3-green)
![Estado](https://img.shields.io/badge/status-Odoo%2019%20Compatible-brightgreen)
![Migrado](https://img.shields.io/badge/migrated-Odoo%2019-orange)

Módulo de localización extendida para República Dominicana que extiende `l10n_do` con funcionalidades avanzadas para cumplir con las regulaciones de la DGII.

> **⚠️ Odoo 19 Migration Notice:** Este módulo ha sido migrado a Odoo 19. Ver [ODOO_19_MIGRATION_NOTES.md](ODOO_19_MIGRATION_NOTES.md) para detalles de los cambios.

## 🚀 Características Principales

### ✅ Gestión de NCF (Números de Comprobante Fiscal)
- ✔️ 10 tipos de NCF (01, 02, 03, 04, 07, 11, 12, 13, 14, 15)
- ✔️ Secuencias automáticas por tipo de comprobante
- ✔️ Validación de formato y rangos
- ✔️ Control de vencimiento de secuencias

### ✅ Impuestos Dominicanos
- ✔️ ITBIS 18%, 16%, 0% (Ventas y Compras)
- ✔️ Retención ITBIS 100%, 75%
- ✔️ Retención ISR 2%, 5%, 10%, 27%
- ✔️ Cálculo automático de retenciones
- ✔️ Configuración por partner

### ✅ Facturación Electrónica (e-CF)
- ✔️ Integración con servicios web DGII
- ✔️ Soporte para certificados digitales (.p12)
- ✔️ Modo pruebas y producción
- ✔️ Generación automática de códigos QR
- ✔️ Gestión avanzada de secuencias NCF
- ✔️ Estados de e-CF (pendiente, enviado, aceptado, rechazado)
- ✔️ TrackID para seguimiento DGII

### ✅ Reportes DGII
- ✔️ Generación de reportes 606 (Compras)
- ✔️ Generación de reportes 607 (Ventas)
- ✔️ Exportación a formato TXT oficial
- ✔️ Wizard de generación por período
- ✔️ Cálculos automáticos de totales

### ✅ Plan Contable
- ✔️ **Estructura de 8 dígitos** (compatible DGII y NIIF)
  - 1 dígito: Categoría (1-Activo, 2-Pasivo, 3-Capital, 4-Ingresos, 5-Costos, 6-Gastos)
  - 2 dígitos: Rubros de agrupación (11-Activo corriente, 21-Pasivo corriente)
  - 4 dígitos: Cuentas de mayor (1101-Efectivo y equivalentes)
  - 6 dígitos: Subcuentas (110101-Caja)
  - 8 dígitos: Cuentas de detalle (11010101-Caja General)
- ✔️ **Más de 70 cuentas preconfiguradas:**
  - Caja general, caja chica
  - Bancos (Popular, BHD, Reservas, Cuentas de ahorro)
  - Clientes nacionales y del exterior
  - Inventarios (mercancías, materia prima, proceso, terminados)
  - ITBIS por cobrar/pagar y por compensar
  - ISR retenido a favor
  - Activos fijos (edificios, maquinaria, transporte, equipos)
  - Proveedores locales y del exterior
  - Retenciones ITBIS e ISR por pagar
  - TSS, AFP, nóminas por pagar
  - Ventas locales y exportación
  - Gastos detallados (personal, alquileres, servicios, etc.)

### ✅ Validaciones Fiscales
- ✔️ Validación de RNC (9 dígitos)
- ✔️ Validación de Cédula (11 dígitos)
- ✔️ Tipos de contribuyente DGII
- ✔️ Clasificación fiscal de partners
- ✔️ Control de datos requeridos

### ✅ Vistas Personalizadas
- ✔️ Configuración fiscal en empresa
- ✔️ Información fiscal en partners
- ✔️ Campos NCF en facturas
- ✔️ Ayuda contextual integrada

## 📋 Requisitos

- Odoo 19.0 Community o Enterprise
- **Módulo `l10n_do`** (Localización base oficial de Odoo - REQUERIDO)
- Módulo `account` (Contabilidad)
- Módulo `account_edi` (Facturación Electrónica)
- Módulo `l10n_latam_base` (Base LATAM)
- Módulo `l10n_latam_invoice_document` (Numeración de documentos LATAM - REQUERIDO)
- Python: `qrcode` (opcional, para códigos QR)

### ⚠️ Importante
Este módulo **extiende** el módulo oficial `l10n_do` de Odoo. Debe instalar primero `l10n_do` antes de instalar `l10n_do_ext`.

### Instalación de Dependencias Opcionales
```bash
pip install qrcode[pil]
```

## 🔧 Instalación

### Paso 1: Instalar Módulo Base (si no está instalado)
1. En Odoo, vaya a **Apps**
2. Busque "**República Dominicana - Accounting**" o "**l10n_do**"
3. Haga clic en **Instalar**

### Paso 2: Instalar Módulo Extendido
1. Copie la carpeta `l10n_do_ext` en su directorio de addons personalizados de Odoo
2. Actualice la lista de aplicaciones en Odoo
3. Busque "**República Dominicana - Contabilidad Extendida**" o "**l10n_do_ext**"
4. Haga clic en **Instalar**

## ⚙️ Configuración

### 1. Configuración de Empresa
1. Vaya a `Ajustes → Empresas → Mi Empresa`
2. Configure el RNC de su empresa (9 dígitos)
3. Seleccione el tipo de contribuyente
4. Configure la fecha de vencimiento de NCF
5. Asigne el diario de compras por defecto

### 2. Configuración de Partners
1. Abra un cliente o proveedor
2. Configure su RNC o Cédula en el campo VAT
3. Seleccione el tipo de identificación
4. Configure el tipo fiscal para ventas (si es cliente)
5. Configure el tipo de gasto y retenciones (si es proveedor)

### 3. Configuración de Diarios
1. Vaya a `Contabilidad → Configuración → Diarios`
2. Configure cada diario con el tipo de documento NCF apropiado
3. Asigne las secuencias NCF a cada diario

### 4. Configuración de Impuestos y Posiciones Fiscales
1. Los impuestos se crean automáticamente al instalar
2. Configure posiciones fiscales en partners según su tipo:
   - **Entidades Gubernamentales**: Posición "Ventas al Estado"
   - **Proveedores Telecomunicaciones**: Posición "Telecomunicaciones"
   - **Proveedores Construcción**: Posición "Materiales de Construcción"
   - **Personas Físicas Servicios**: Posición "Persona Física - Servicios"
   - **Proveedores Exterior**: Posición "Servicios al Exterior"
3. Los impuestos se aplicarán automáticamente según la posición fiscal

## 📊 Tipos de NCF Soportados

| Código | Nombre | Uso |
|--------|--------|-----|
| 01 | Factura de Crédito Fiscal | Ventas a contribuyentes |
| 02 | Factura de Consumo | Ventas a consumidores finales |
| 03 | Nota de Débito | Ajustes positivos |
| 04 | Nota de Crédito | Devoluciones/ajustes negativos |
| 07 | Comprobante de Retención | Retenciones realizadas |
| 11 | Comprobante de Compras | Compras informales |
| 12 | Registro Único de Ingresos | Ingresos únicos |
| 13 | Gastos Menores | Gastos sin NCF formal |
| 14 | Régimen Especial | Operaciones especiales |
| 15 | Gubernamental | Ventas al gobierno |

## 💰 Impuestos y Grupos Especializados

### ITBIS (IVA)
- **18%**: Tasa estándar actual (ventas y compras)
- **16%**: Tasa reducida (ventas y compras)
- **0%**: Exento/No gravado (ventas y compras)

### Retenciones ITBIS
- **100%**: Retención completa del ITBIS
- **75%**: Retención parcial (construcción)

### Retenciones ISR
- **2%**: Retención básica
- **5%**: Retención servicios
- **10%**: Retención estándar (profesionales, alquileres)
- **27%**: Retención personas físicas y servicios al exterior

### Grupos de Impuestos Especializados
- **Telecomunicaciones**: ITBIS 18% + Retención ISR 10%
- **Materiales de Construcción**: ITBIS 18% + Retención ITBIS 75%
- **Servicios Profesionales**: ITBIS 18% + Retención ISR 10%
- **Persona Física Servicios**: Retención ISR 27% (sin ITBIS)
- **Alquileres**: Retención ISR 10%
- **Servicios al Exterior**: Retención ISR 27%
- **Ventas al Estado**: ITBIS 0% (exento)

### Posiciones Fiscales (Automatización)
Las posiciones fiscales permiten aplicar automáticamente los impuestos correctos según el tipo de partner:
- **Ventas al Estado (Exentas)**: Cambia ITBIS 18%/16% → ITBIS 0%
- **Servicios al Exterior**: Aplica Retención ISR 27%
- **Persona Física - Servicios**: Aplica Retención ISR 27%
- **Telecomunicaciones**: Aplica ITBIS 18% + Retención ISR 10%
- **Materiales de Construcción**: Aplica ITBIS 18% + Retención ITBIS 75%
- **Servicios Profesionales**: Aplica ITBIS 18% + Retención ISR 10%
- **Alquileres**: Aplica Retención ISR 10%

## 📝 Uso

### Emitir una Factura
1. Cree una nueva factura de cliente
2. El sistema seleccionará automáticamente el tipo de NCF según el cliente
3. Complete los productos/servicios
4. Los impuestos se aplicarán automáticamente
5. Al confirmar, se generará el NCF automáticamente

### Registrar una Compra
1. Cree una factura de proveedor
2. Ingrese el NCF del proveedor
3. Configure las retenciones si aplican
4. Los impuestos se calcularán automáticamente
5. Confirme la factura

## ⚠️ Consideraciones Importantes

### Legales
- Debe solicitar secuencias NCF autorizadas por la DGII
- Configure los rangos de NCF correctamente
- Verifique que sus reportes cumplan con DGII
- Consulte con un contador para su caso específico

### Técnicas
- Haga backups regulares de su base de datos
- Pruebe en un entorno de desarrollo primero
- Mantenga el módulo actualizado
- Revise los logs de Odoo ante cualquier error

## 🏗️ Estructura del Módulo

```
l10n_do_ext/
├── __init__.py
├── __manifest__.py
├── README.md
├── data/
│   ├── __init__.py
│   ├── l10n_do_chart_template.xml            # Plan contable base (6 dígitos)
│   ├── l10n_do_chart_template_extended.xml   # Plan contable extendido (8 dígitos)
│   ├── l10n_do_taxes.xml                     # Impuestos básicos
│   ├── l10n_do_taxes_advanced.xml            # Impuestos especializados
│   ├── l10n_do_fiscal_positions.xml          # Posiciones fiscales
│   └── l10n_do_ncf_sequences.xml             # Secuencias NCF (10 tipos)
├── models/
│   ├── __init__.py
│   ├── res_company.py                        # Extensión de empresa + e-CF
│   ├── res_partner.py                        # Extensión de partners
│   ├── res_config_settings.py                # Configuración e-CF
│   ├── account_move.py                       # Extensión de facturas + QR
│   ├── l10n_do_dgii_report.py                # Reportes 606/607
│   └── l10n_do_ncf_manager.py                # Gestión secuencias + QR
├── views/
│   ├── res_company_views.xml                 # Vistas de empresa
│   ├── res_partner_views.xml                 # Vistas de partners
│   ├── res_config_settings_views.xml         # Configuración e-CF
│   ├── account_move_views.xml                # Vistas de facturas
│   └── l10n_do_dgii_report_views.xml         # Vistas reportes DGII
├── wizard/
│   ├── __init__.py
│   ├── l10n_do_dgii_report_wizard.py         # Wizard reportes DGII
│   ├── l10n_do_dgii_report_wizard_views.xml
│   ├── l10n_do_config_wizard.py              # Wizard configuración
│   └── l10n_do_config_wizard_views.xml
├── security/
│   └── ir.model.access.csv                   # Permisos (12 reglas)
├── demo/
│   └── demo_data.xml                         # Datos de prueba
└── static/
    └── description/
        ├── index.html                        # Descripción HTML
        ├── icon.svg                          # Ícono SVG
        └── banner.svg                        # Banner SVG
```

## 📚 Recursos

- [Portal DGII](https://dgii.gov.do)
- [Legislación Tributaria RD](https://dgii.gov.do/legislacion)
- [Información sobre NCF](https://dgii.gov.do/ncf)
- [Odoo Documentation](https://www.odoo.com/documentation/19.0)

## 🤝 Soporte

Para soporte técnico o consultas:
- Reporte issues en el repositorio del proyecto
- Contacte a su partner de implementación de Odoo
- Consulte la documentación oficial de Odoo

## 📄 Licencia

Este módulo está licenciado bajo LGPL-3.

## 🔄 Historial de Versiones

### 19.0.1.0.0 (2025)
- ✨ Versión inicial para Odoo 19
- ✨ 10 tipos de NCF implementados con gestión avanzada
- ✨ Plan contable con estructura de 8 dígitos (70+ cuentas)
- ✨ Compatible DGII y NIIF
- ✨ 20+ impuestos y grupos especializados
- ✨ 8 posiciones fiscales para automatización
- ✨ Retenciones ISR e ITBIS automáticas
- ✨ Reportes DGII 606 y 607 con exportación TXT
- ✨ Facturación electrónica (e-CF) base preparada
- ✨ Generación de códigos QR
- ✨ Validaciones RNC/Cédula
- ✨ Vistas personalizadas
- ✨ Datos demo para pruebas
- ✨ Documentación completa HTML + README

## 👨‍💻 Autor

**Tu Nombre / Tu Empresa**
- Website: https://www.tu-web.com
- Email: contacto@tu-web.com

---

**Nota:** Este módulo es la base para implementar facturación electrónica (e-CF) según los requisitos de la DGII.

