# Archivos de Descripción del Módulo

Esta carpeta contiene los archivos visuales que se muestran en Odoo Apps.

## Archivos Incluidos

### 📄 index.html
**Descripción completa del módulo** que se muestra cuando se hace clic en el módulo en Apps.

- Diseño profesional con colores de la bandera dominicana
- Características completas
- Tipos de e-CF soportados
- Requisitos y dependencias
- Guía de instalación
- Tablas de información
- Alertas y avisos importantes

### 🎨 icon.svg
**Icono del módulo** que aparece en el listado de Apps.

- Tamaño: 128x128 px
- Diseño: Documento e-CF con código QR
- Colores: Azul (#002D62) y Rojo (#C60C30) de la bandera RD
- Formato: SVG (escalable)

### 🖼️ banner.svg
**Banner principal** que se muestra en la parte superior de la descripción.

- Tamaño: 800x200 px
- Diseño: Flujo de proceso e-CF (Genera → Firma → Envía → Aprobado)
- Elementos: Documentos, certificado, nube DGII, checkmark de aprobación
- Formato: SVG (escalable)

## Personalización

Si deseas personalizar los colores o el diseño:

1. **Editar index.html:** Modificar los estilos CSS en la sección `<style>`
2. **Editar icon.svg:** Cambiar colores en los atributos `fill` y `stroke`
3. **Editar banner.svg:** Ajustar elementos SVG y texto

## Colores Oficiales RD

- **Azul:** #002D62 (Libertad)
- **Rojo:** #C60C30 (Sangre de héroes)
- **Blanco:** #FFFFFF (Paz)

## Conversión a PNG (Opcional)

Si prefieres usar PNG en lugar de SVG:

```bash
# Instalar imagemagick o inkscape
# Windows:
choco install imagemagick

# Convertir
magick icon.svg icon.png
magick banner.svg banner.png
```

Luego actualizar `__manifest__.py`:
```python
'images': [
    'static/description/banner.png',
    'static/description/icon.png',
],
```

## Vista Previa

Para ver cómo se verá en Odoo:

1. Instalar el módulo
2. Ir a Apps
3. Buscar "Facturación Electrónica"
4. Ver el icono en la lista
5. Hacer clic en el módulo para ver la descripción completa

## Optimización

Los archivos SVG son:
- ✅ Escalables sin pérdida de calidad
- ✅ Ligeros (pocos KB)
- ✅ Soportados nativamente en Odoo 19
- ✅ Editables con cualquier editor de texto
- ✅ Compatibles con navegadores modernos

No es necesario convertirlos a PNG a menos que haya problemas de compatibilidad específicos.

