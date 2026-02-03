FROM odoo:19

USER root

# Instalar dependencias del sistema necesarias para xmlsec y otras librerías
# Agregamos libxslt1-dev para que lxml compile correctamente
RUN apt-get update && apt-get install -y \
    pkg-config \
    libxml2-dev \
    libxslt1-dev \
    libxmlsec1-dev \
    libxmlsec1-openssl \
    libpython3-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements si existiera un archivo separado, o instalar directo
# Forzamos la compilación de lxml y xmlsec desde fuente para evitar mismatch de libxml2
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

# Crear directorio de addons extra
RUN mkdir -p /mnt/extra-addons

# Copiar addons y configuración dentro de la imagen
COPY ./custom_addons /mnt/extra-addons
COPY ./config/odoo.conf /etc/odoo/odoo.conf

# Ajustar permisos
RUN chown -R odoo:odoo /mnt/extra-addons
RUN chown odoo:odoo /etc/odoo/odoo.conf

USER odoo
