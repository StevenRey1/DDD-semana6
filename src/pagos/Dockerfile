FROM python:3.11-slim

# Instalar herramientas del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . /app/

# Configurar variables de entorno
ENV PYTHONPATH=/app

# Crear usuario no-root para seguridad
RUN groupadd -r pagos && useradd -r -g pagos pagos
RUN chown -R pagos:pagos /app
USER pagos

# Exponer puerto
EXPOSE 8080

# Comando por defecto
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]