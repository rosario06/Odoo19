FROM odoo:19

USER root

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    pkg-config \
    libxml2-dev \
    libxslt1-dev \
    libxmlsec1-dev \
    libxmlsec1-openssl \
    libpython3-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
RUN pip3 install --no-cache-dir --break-system-packages \
    --no-binary lxml,xmlsec \
    zeep \
    xmlsec \
    cryptography \
    qrcode \
    pillow \
    lxml \
    requests \
    requests-toolbelt \
    xmlschema \
    xlsxwriter

# Crear directorio de addons extra en una ruta alternativa
RUN mkdir -p /opt/odoo/custom_addons

# Copiar addons y configuración dentro de la imagen
# Usamos un comodín para asegurar que copiamos el contenido
COPY custom_addons/ /opt/odoo/custom_addons/
COPY config/odoo.conf /etc/odoo/odoo.conf

# Ajustar permisos explícitamente para el usuario odoo
RUN chown -R odoo:odoo /opt/odoo/custom_addons && \
    chmod -R 755 /opt/odoo/custom_addons && \
    chown odoo:odoo /etc/odoo/odoo.conf

USER odoo
