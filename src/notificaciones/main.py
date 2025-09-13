"""
Microservicio de Notificaciones - FastAPI
Implementa patrones DDD, CQRS y arquitectura hexagonal
"""

import asyncio
import logging
import sys
import os
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any

# Agregar el directorio raíz al path para importaciones absolutas
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from notificaciones.config import configuracion
from notificaciones.modulos.aplicacion.servicios import ServicioAplicacionNotificaciones
from notificaciones.modulos.aplicacion.dto import (
    NotificacionDTO,
    CrearNotificacionDTO, 
    ListaNotificacionesDTO,
    EstadisticasNotificacionesDTO
)
from notificaciones.modulos.aplicacion.queries.obtener_notificaciones import (
    ObtenerTodasNotificaciones,
    ObtenerTodasNotificacionesHandler,
    ConsultaObtenerEstadisticasNotificaciones,
    ManejadorObtenerEstadisticasNotificaciones
)
# from notificaciones.modulos.infraestructura.repositorios import RepositorioNotificacionesMemoria  # 🔄 TEMPORAL: Hasta solucionar red
from notificaciones.modulos.infraestructura.repositorio_postgresql import RepositorioNotificacionesPostgreSQL
from notificaciones.modulos.infraestructura.despachadores import DespachadorEventos
from notificaciones.modulos.infraestructura.consumidores import OrquestadorConsumidores


# Configuración de logging
logging.basicConfig(
    level=getattr(logging, configuracion.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Instancias globales
repositorio_notificaciones = RepositorioNotificacionesPostgreSQL()  # 🐘 USANDO POSTGRESQL
despachador_eventos = DespachadorEventos()
servicio_notificaciones = ServicioAplicacionNotificaciones(
    repositorio_notificaciones,
    despachador_eventos
)
orquestador_consumidores = OrquestadorConsumidores(servicio_notificaciones)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestiona el ciclo de vida de la aplicación"""
    # Startup
    logger.info("Iniciando aplicación de notificaciones")
    
    try:
        # Inicializar repositorio PostgreSQL
        await repositorio_notificaciones.inicializar()
        logger.info("Repositorio PostgreSQL inicializado")
        
        # Inicializar despachador de eventos
        await despachador_eventos.inicializar()
        logger.info("Despachador de eventos inicializado")
        
        # Iniciar consumidores de eventos
        await orquestador_consumidores.iniciar_todos()
        logger.info("Consumidores de eventos iniciados")
        
        logger.info("Aplicación iniciada exitosamente")
        
        yield
        
    except Exception as e:
        logger.error(f"Error durante el startup: {e}")
        yield
        
    finally:
        # Shutdown
        logger.info("Cerrando aplicación de notificaciones")
        
        try:
            # Detener consumidores
            await orquestador_consumidores.detener_todos()
            logger.info("Consumidores detenidos")
            
            # Cerrar despachador
            await despachador_eventos.cerrar()
            logger.info("Despachador cerrado")
            
            # Cerrar repositorio PostgreSQL
            await repositorio_notificaciones.cerrar()
            logger.info("Repositorio PostgreSQL cerrado")
            
        except Exception as e:
            logger.error(f"Error durante el shutdown: {e}")
        
        logger.info("Aplicación cerrada exitosamente")


# Crear aplicación FastAPI
app = FastAPI(
    title="API de Notificaciones",
    description="Microservicio para gestión de notificaciones usando DDD y CQRS",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)


# Modelos de respuesta específicos para la API
class RespuestaAPI(BaseModel):
    """Respuesta base de la API"""
    exito: bool
    mensaje: str
    datos: Optional[Any] = None


class CrearNotificacionRequest(BaseModel):
    """Request para crear notificación"""
    id_usuario: str = Field(..., description="ID del usuario")
    tipo: str = Field(..., description="Tipo de notificación: transaccional, promocional, alerta, bienvenida, recompensa")
    canal: str = Field(..., description="Canal: email, sms, push")
    destinatario: str = Field(..., description="Email, teléfono o token de dispositivo")
    titulo: str = Field(..., description="Título de la notificación")
    mensaje: str = Field(..., description="Mensaje de la notificación")
    datos_adicionales: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Datos adicionales")


class MarcarFallidaRequest(BaseModel):
    """Request para marcar notificación como fallida"""
    error: str = Field(..., description="Descripción del error")


# Dependency injection
async def obtener_servicio_notificaciones() -> ServicioAplicacionNotificaciones:
    """Proveedor del servicio de aplicación"""
    return servicio_notificaciones


# Endpoints de la API

@app.get("/", response_model=RespuestaAPI)
async def root():
    """Endpoint raíz"""
    return RespuestaAPI(
        exito=True,
        mensaje="API de Notificaciones funcionando correctamente",
        datos={"version": "1.0.0", "servicio": "notificaciones"}
    )


@app.get("/health", response_model=RespuestaAPI)
async def health_check():
    """Verificación de salud del servicio"""
    try:
        # Verificar conexiones
        total_notificaciones = await repositorio_notificaciones.contar_total()
        
        return RespuestaAPI(
            exito=True,
            mensaje="Servicio saludable",
            datos={
                "status": "healthy",
                "total_notificaciones": total_notificaciones,
                "pulsar_connected": despachador_eventos.client is not None and despachador_eventos.esta_conectado
            }
        )
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return RespuestaAPI(
            exito=False,
            mensaje=f"Servicio con problemas: {e}",
            datos={"status": "unhealthy"}
        )


@app.post("/notificaciones", response_model=RespuestaAPI, status_code=status.HTTP_201_CREATED)
async def crear_notificacion(
    request: CrearNotificacionRequest,
    background_tasks: BackgroundTasks,
    servicio: ServicioAplicacionNotificaciones = Depends(obtener_servicio_notificaciones)
):
    """Crea una nueva notificación"""
    try:
        dto = CrearNotificacionDTO(
            id_usuario=request.id_usuario,
            tipo=request.tipo,
            canal=request.canal,
            destinatario=request.destinatario,
            titulo=request.titulo,
            mensaje=request.mensaje,
            datos_adicionales=request.datos_adicionales
        )
        
        notificacion = await servicio.crear_notificacion(dto)
        
        # Procesar envío en background
        if request.tipo != "borrador":
            background_tasks.add_task(
                _enviar_notificacion_background,
                notificacion.id_notificacion,
                servicio
            )
        
        return RespuestaAPI(
            exito=True,
            mensaje="Notificación creada exitosamente",
            datos=notificacion.to_dict()
        )
        
    except Exception as e:
        logger.error(f"Error creando notificación: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


async def _enviar_notificacion_background(id_notificacion: str, servicio: ServicioAplicacionNotificaciones):
    """Envía notificación en background"""
    try:
        await asyncio.sleep(1)  # Simular procesamiento
        await servicio.enviar_notificacion(id_notificacion)
        logger.info(f"Notificación {id_notificacion} enviada en background")
    except Exception as e:
        logger.error(f"Error enviando notificación {id_notificacion}: {e}")
        await servicio.marcar_notificacion_fallida(id_notificacion, str(e))


@app.get("/notificaciones/{id_notificacion}", response_model=RespuestaAPI)
async def obtener_notificacion(
    id_notificacion: str,
    servicio: ServicioAplicacionNotificaciones = Depends(obtener_servicio_notificaciones)
):
    """Obtiene una notificación por su ID"""
    try:
        notificacion = await servicio.obtener_notificacion(id_notificacion)
        
        if not notificacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notificación no encontrada"
            )
        
        return RespuestaAPI(
            exito=True,
            mensaje="Notificación obtenida exitosamente",
            datos=notificacion.to_dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo notificación: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@app.get("/usuarios/{id_usuario}/notificaciones", response_model=RespuestaAPI)
async def obtener_notificaciones_usuario(
    id_usuario: str,
    limite: int = 50,
    offset: int = 0,
    servicio: ServicioAplicacionNotificaciones = Depends(obtener_servicio_notificaciones)
):
    """Obtiene las notificaciones de un usuario"""
    try:
        notificaciones = await servicio.obtener_notificaciones_usuario(
            id_usuario, limite, offset
        )
        
        return RespuestaAPI(
            exito=True,
            mensaje="Notificaciones obtenidas exitosamente",
            datos=notificaciones.to_dict()
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo notificaciones del usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@app.put("/notificaciones/{id_notificacion}/enviar", response_model=RespuestaAPI)
async def enviar_notificacion(
    id_notificacion: str,
    servicio: ServicioAplicacionNotificaciones = Depends(obtener_servicio_notificaciones)
):
    """Envía una notificación pendiente"""
    try:
        notificacion = await servicio.enviar_notificacion(id_notificacion)
        
        return RespuestaAPI(
            exito=True,
            mensaje="Notificación enviada exitosamente",
            datos=notificacion.to_dict()
        )
        
    except Exception as e:
        logger.error(f"Error enviando notificación: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.put("/notificaciones/{id_notificacion}/marcar-fallida", response_model=RespuestaAPI)
async def marcar_notificacion_fallida(
    id_notificacion: str,
    request: MarcarFallidaRequest,
    servicio: ServicioAplicacionNotificaciones = Depends(obtener_servicio_notificaciones)
):
    """Marca una notificación como fallida"""
    try:
        notificacion = await servicio.marcar_notificacion_fallida(
            id_notificacion, 
            request.error
        )
        
        return RespuestaAPI(
            exito=True,
            mensaje="Notificación marcada como fallida",
            datos=notificacion.to_dict()
        )
        
    except Exception as e:
        logger.error(f"Error marcando notificación como fallida: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.get("/notificaciones", response_model=RespuestaAPI)
async def listar_notificaciones(
    limite: int = 100,
    offset: int = 0,
    estado: Optional[str] = None,
    tipo: Optional[str] = None,
    canal: Optional[str] = None,
    servicio: ServicioAplicacionNotificaciones = Depends(obtener_servicio_notificaciones)
):
    """Lista notificaciones con filtros opcionales"""
    try:
        if estado == "pendientes":
            notificaciones = await servicio.obtener_notificaciones_pendientes()
            return RespuestaAPI(
                exito=True,
                mensaje="Notificaciones pendientes obtenidas",
                datos={"items": [n.to_dict() for n in notificaciones], "total": len(notificaciones)}
            )
        
        # Para otros filtros, usar el repositorio directamente
        todas = await repositorio_notificaciones.obtener_todas(limite, offset)
        
        # Aplicar filtros
        if estado:
            todas = [n for n in todas if n.estado.valor == estado]
        if tipo:
            todas = [n for n in todas if n.tipo.valor == tipo]
        if canal:
            todas = [n for n in todas if n.canal.valor == canal]
        
        # Convertir a DTOs
        from .modulos.aplicacion.mapeadores import MapeadorNotificacion
        mapeador = MapeadorNotificacion()
        dtos = [mapeador.entidad_a_dto(n) for n in todas]
        
        return RespuestaAPI(
            exito=True,
            mensaje="Notificaciones listadas exitosamente",
            datos={"items": [d.to_dict() for d in dtos], "total": len(dtos)}
        )
        
    except Exception as e:
        logger.error(f"Error listando notificaciones: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@app.get("/estadisticas", response_model=RespuestaAPI)
async def obtener_estadisticas(
    servicio: ServicioAplicacionNotificaciones = Depends(obtener_servicio_notificaciones)
):
    """Obtiene estadísticas de notificaciones"""
    try:
        estadisticas = await servicio.obtener_estadisticas()
        
        return RespuestaAPI(
            exito=True,
            mensaje="Estadísticas obtenidas exitosamente",
            datos=estadisticas.to_dict()
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@app.post("/procesar-pendientes", response_model=RespuestaAPI)
async def procesar_notificaciones_pendientes(
    background_tasks: BackgroundTasks,
    servicio: ServicioAplicacionNotificaciones = Depends(obtener_servicio_notificaciones)
):
    """Procesa todas las notificaciones pendientes en background"""
    try:
        # Obtener pendientes
        pendientes = await servicio.obtener_notificaciones_pendientes()
        
        # Procesar en background
        for notif in pendientes:
            background_tasks.add_task(
                _enviar_notificacion_background,
                notif.id_notificacion,
                servicio
            )
        
        return RespuestaAPI(
            exito=True,
            mensaje=f"Se han programado {len(pendientes)} notificaciones para envío",
            datos={"programadas": len(pendientes)}
        )
        
    except Exception as e:
        logger.error(f"Error procesando notificaciones pendientes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


if __name__ == "__main__":
    uvicorn.run(
        "notificaciones.main:app",
        host="0.0.0.0",
        port=5000,
        reload=configuracion.debug,
        log_level=configuracion.log_level.lower()
    )
