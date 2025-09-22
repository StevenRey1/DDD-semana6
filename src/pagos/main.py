from fastapi import FastAPI
from presentacion.api import router
from config.db import create_tables
from config.pulsar_config import Settings
import threading

    # ✅ Importar módulo para auto-registro de handlers CQRS
import modulos.aplicacion.comandos.pago_command_handler
import modulos.aplicacion.queries.obtener_estado_pago_handler

# ✅ Importar consumer de comando-pago
from modulos.infraestructura.comando_pago_consumer import main_comando_pago_consumer

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
    
    # ✅ Iniciar consumer de comando-pago en hilo separado
    print("🔄 Iniciando consumer de comando-pago...")
    comando_consumer_thread = threading.Thread(target=main_comando_pago_consumer, daemon=True)
    comando_consumer_thread.start()
    print("✅ Consumer de comando-pago iniciado en hilo separado")

app.include_router(router)
