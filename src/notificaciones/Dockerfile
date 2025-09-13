# Dockerfile para el Microservicio de Notificaciones
# Basado en Python 3.10 slim para optimizar tamaño

FROM python:3.10-slim

# Etiquetas del contenedor
LABEL maintainer="AlpesPartners Team"
LABEL service="notificaciones"
LABEL version="1.0.0"
LABEL description="Microservicio de Notificaciones - DDD Architecture"

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Crear usuario no-root para seguridad
RUN groupadd -r notificaciones && useradd -r -g notificaciones notificaciones

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
COPY src/notificaciones/requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY src/notificaciones/ /app/src/notificaciones/

# Copiar y hacer ejecutable el entrypoint
COPY src/notificaciones/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Crear directorios necesarios
RUN mkdir -p /app/logs /app/data

# Cambiar permisos
RUN chown -R notificaciones:notificaciones /app

# Cambiar al usuario no-root
USER notificaciones

# Variables de entorno del microservicio
ENV AMBIENTE=produccion
ENV DEBUG=false
ENV LOG_LEVEL=INFO

# Variables de entorno para Pulsar
ENV PULSAR_HOST=pulsar
ENV PULSAR_PORT=6650
ENV PULSAR_TENANT=public
ENV PULSAR_NAMESPACE=default
ENV PULSAR_SUBSCRIPTION=notificaciones-sub

# Variables de entorno para Base de Datos
ENV DATABASE_URL=postgresql://postgres:postgres123@postgres:5432/alpespartners

# Configuración de canales de notificación
ENV EMAIL_HABILITADO=true
ENV SMS_HABILITADO=true
ENV PUSH_HABILITADO=true

# Exponer el puerto
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Configurar entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Comando por defecto
CMD ["python", "-m", "uvicorn", "src.notificaciones.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8002", \
     "--workers", "1", \
     "--access-log", \
     "--log-level", "info"]