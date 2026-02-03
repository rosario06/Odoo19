FROM odoo:19

USER root

# Instalar dependencias del sistema necesarias para xmlsec y otras librerías
RUN apt-get update && apt-get install -y \
    pkg-config \
    libxml2-dev \
    libxmlsec1-dev \
    libxmlsec1-openssl \
    libpython3-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements si existiera un archivo separado, o instalar directo
# Dependencias extraídas de requirements.txt de l10n_do_ecf
# Usamos --break-system-packages porque Odoo 19 usa Python reciente en entorno gestionado
RUN pip3 install --no-cache-dir --break-system-packages \
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

USER odoo
