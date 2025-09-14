from fastapi import FastAPI
from .presentacion.api import router
from .modulos.infraestructura.repositorio_postgresql import RepositorioPagosPG
from .config.pulsar_config import settings

app = FastAPI(title="API de Pagos", version="1.0.0")

@app.on_event("startup")
def on_startup():
    repo = RepositorioPagosPG(settings.DB_URL)
    repo.init_db()
    app.state.repo = repo

app.include_router(router)
