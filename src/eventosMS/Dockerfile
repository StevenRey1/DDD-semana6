FROM python:3.11-slim
WORKDIR /app
COPY src/eventosMS/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copia todo el código fuente
COPY . /app/
ENV PYTHONPATH=/app/src
EXPOSE 8003
# Comando para ejecutar la app Flask
CMD ["python", "-m", "flask", "--app", "src/eventosMS/api", "run", "--host=0.0.0.0", "--port=8003"]