FROM python:3.11-slim
WORKDIR /app
COPY src/referidos/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copia todo el código fuente
COPY . /app/
ENV PYTHONPATH=/app/src
EXPOSE 8004
# Comando para ejecutar la app Flask
CMD ["python", "-u", "-m", "flask", "--app", "src/referidos/api", "run", "--host=0.0.0.0", "--port=8004"]