# Dockerfile para el Microservicio de Referidos
# Basado en Python 3.10 slim para optimizar tamaño

FROM python:3.10-slim

# Etiquetas del contenedor
LABEL maintainer="AlpesPartners Team"
LABEL service="referidos"
LABEL version="1.0.0"
LABEL description="Microservicio de Referidos - DDD Architecture"

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app:/app/src/referidos

# Crear usuario no-root para seguridad
RUN groupadd -r referidos && useradd -r -g referidos referidos

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY src/referidos/requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY src/referidos/ /app/src/referidos/

# Copiar y hacer ejecutable el entrypoint
COPY src/referidos/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Crear directorios necesarios
RUN mkdir -p /app/logs /app/data

# Cambiar permisos
RUN chown -R referidos:referidos /app

# Cambiar al usuario no-root
USER referidos

# Variables de entorno del microservicio
ENV AMBIENTE=produccion
ENV DEBUG=false
ENV LOG_LEVEL=INFO

# Variables de entorno para Flask
ENV FLASK_APP=src.referidos.api:create_app
ENV FLASK_ENV=production
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=5001

# Variables de entorno para Pulsar
ENV PULSAR_HOST=pulsar
ENV PULSAR_PORT=6650
ENV PULSAR_TENANT=public
ENV PULSAR_NAMESPACE=default
ENV PULSAR_SUBSCRIPTION=referidos-sub

# Variables de entorno para Base de Datos
ENV DATABASE_URL=sqlite:///app/src/referidos/api/database.db

# Configuración de canales
ENV EVENTOS_HABILITADOS=true
ENV INTEGRACION_HABILITADA=true

# Exponer el puerto
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

# Configurar entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Comando por defecto para ejecutar Flask
CMD ["python", "-m", "flask", "run", \
     "--host", "0.0.0.0", \
     "--port", "5001"]