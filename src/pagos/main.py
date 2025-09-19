from fastapi import FastAPI
from presentacion.api import router
from config.db import create_tables
from config.pulsar_config import Settings

# ✅ Importar módulo para auto-registro de handlers CQRS
import modulos.aplicacion.comandos.pago_command_handler
import modulos.aplicacion.queries.obtener_estado_pago_handler

app = FastAPI(title="API de Pagos", version="1.0.0")

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "pagos"}

@app.on_event("startup")
def on_startup():
    print("🚀 Iniciando servicio de Pagos...")
    create_tables()
    print("✅ Base de datos inicializada")
    print("🎯 Handlers CQRS cargados y listos")

app.include_router(router)
