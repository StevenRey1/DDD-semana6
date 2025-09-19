from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from contextlib import asynccontextmanager
from collections import deque  # Para thread-safe queue

from pydantic_settings import BaseSettings
from typing import Any

from .consumidores import suscribirse_a_topico
from .api.v1.router import schema
from strawberry.fastapi import GraphQLRouter
from sse_starlette.sse import EventSourceResponse

# Crear GraphQL router directamente
graphql_app = GraphQLRouter(schema)

class Config(BaseSettings):
    APP_VERSION: str = "1"

settings = Config()
app_configs: dict[str, Any] = {"title": "BFF-Web Alpespartners", "version": settings.APP_VERSION}

# Usar deque para thread-safe operations
eventos_queue = deque()
tasks = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Iniciando consumidor de eventos...")
    task1 = asyncio.ensure_future(
        suscribirse_a_topico(
            "eventos-tracking",
            "alpespartners-bff",
            "public/default/eventos-tracking",
            eventos=eventos_queue
        )
    )
    tasks.append(task1)
    yield

    print("🛑 Cancelando tareas...")
    for task in tasks:
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

app = FastAPI(lifespan=lifespan, **app_configs)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En desarrollo permitir todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir GraphQL router
app.include_router(graphql_app, prefix="/v1/graphql")
# Incluir API v1 router - TODO: implementar router REST
# app.include_router(v1, prefix="/v1")

@app.get('/stream')
async def stream_mensajes(request: Request):
    print(f"🔄 Nueva conexión SSE establecida")

    async def generar_eventos():
        try:
            while True:
                # Si el cliente cierra la conexión
                if await request.is_disconnected():
                    print(f"🔌 Conexión SSE cerrada por cliente")
                    break

                # Procesar eventos en orden (FIFO)
                if eventos_queue:
                    try:
                        evento = eventos_queue.popleft()  # Primer elemento
                        print(f"📤 Enviando evento vía SSE: {evento}")

                        # Formato SSE correcto - serializar como JSON
                        mensaje_sse = f"data: {json.dumps(evento)}\n\n"
                        yield mensaje_sse
                    except IndexError:
                        continue
                else:
                    # Enviar keep-alive
                    yield "data: ping\n\n"
                    await asyncio.sleep(3)

                await asyncio.sleep(0.1)

        except Exception as e:
            print(f"❌ Error en SSE: {e}")
            yield ": error\n\n"

    return EventSourceResponse(
        generar_eventos(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
        }
    )


# app.include_router(v1, prefix="/v1")  # Comentado porque no está implementado