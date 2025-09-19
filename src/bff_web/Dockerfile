# Este Dockerfile está ubicado en: src/bff_web/Dockerfile

FROM python:3.12-slim

WORKDIR /app

# La ruta a requirements.txt es relativa al contexto de compilación (la raíz del proyecto)
COPY src/bff_web/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el contenido de la carpeta 'src' al WORKDIR del contenedor.
COPY src/. .

# =================================================================
#               AÑADE ESTA LÍNEA DE DIAGNÓSTICO
# =================================================================
# Este comando listará todos los archivos y carpetas en /app
# para que podamos VERIFICAR que main.py está ahí durante la compilación.
RUN ls -laR /app
# =================================================================

EXPOSE 8000

CMD ["uvicorn", "bff_web.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]