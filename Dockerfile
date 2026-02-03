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

# Crear directorio de addons extra (vacío, se montará desde volumen)
RUN mkdir -p /mnt/extra-addons && chown -R odoo:odoo /mnt/extra-addons

# Copiar solo la configuración
COPY ./config/odoo.conf /etc/odoo/odoo.conf
RUN chown odoo:odoo /etc/odoo/odoo.conf

USER odoo
