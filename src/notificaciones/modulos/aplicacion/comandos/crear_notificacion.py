from dataclasses import dataclass
from typing import Optional, Dict, Any

from .base import Comando, ComandoHandler
from ..dto import NotificacionDTO
from ...dominio.repositorios import RepositorioNotificaciones
from ...dominio.fabricas import FabricaNotificaciones
from ...dominio.entidades import Notificacion
from ...infraestructura.despachadores import DespachadorEventos


@dataclass
class ComandoCrearNotificacion(Comando):
    """Comando para crear una nueva notificación"""
    id_usuario: str
    tipo: str
    mensaje: str
    canal: str
    destinatario: Optional[str] = None
    titulo: Optional[str] = None
    datos_adicionales: Optional[Dict[str, Any]] = None


class ManejadorCrearNotificacion(ComandoHandler):
    """Handler para el comando de crear notificación"""
    
    def __init__(
        self,
        repositorio_notificaciones: RepositorioNotificaciones,
        despachador_eventos: DespachadorEventos
    ):
        self.repositorio_notificaciones = repositorio_notificaciones
        self.despachador_eventos = despachador_eventos
    
    async def handle(self, comando: ComandoCrearNotificacion) -> Notificacion:
        """Maneja la creación de una nueva notificación"""
        
        # Crear la notificación usando la fábrica
        notificacion = FabricaNotificaciones.crear_desde_datos({
            "id_usuario": comando.id_usuario,
            "tipo": comando.tipo,
            "mensaje": comando.mensaje,
            "canal": comando.canal,
            "destinatario": comando.destinatario,
            "titulo": comando.titulo,
            "datos_adicionales": comando.datos_adicionales
        })
        
        # Persistir la notificación
        await self.repositorio_notificaciones.agregar(notificacion)
        
        # Publicar eventos de dominio
        for evento in notificacion.eventos:
            await self.despachador_eventos.publicar_evento(evento)
        
        # Limpiar eventos después de publicarlos
        notificacion.limpiar_eventos()
        
        return notificacion


@dataclass
class ComandoEnviarNotificacion(Comando):
    """Comando para marcar una notificación como enviada"""
    id_notificacion: str


class ManejadorEnviarNotificacion(ComandoHandler):
    """Handler para el comando de enviar notificación"""
    
    def __init__(
        self,
        repositorio_notificaciones: RepositorioNotificaciones,
        despachador_eventos: DespachadorEventos
    ):
        self.repositorio_notificaciones = repositorio_notificaciones
        self.despachador_eventos = despachador_eventos
    
    async def handle(self, comando: ComandoEnviarNotificacion) -> Notificacion:
        """Maneja el envío de una notificación"""
        
        # Obtener la notificación
        notificacion = await self.repositorio_notificaciones.obtener_por_id(comando.id_notificacion)
        
        if not notificacion:
            raise ValueError(f"Notificación {comando.id_notificacion} no encontrada")
        
        # Marcar como enviada
        notificacion.marcar_como_enviada()
        
        # Actualizar en el repositorio
        await self.repositorio_notificaciones.actualizar(notificacion)
        
        # Publicar eventos de dominio
        for evento in notificacion.eventos:
            await self.despachador_eventos.publicar_evento(evento)
        
        # Limpiar eventos
        notificacion.limpiar_eventos()
        
        return notificacion


@dataclass
class ComandoMarcarNotificacionFallida(Comando):
    """Comando para marcar una notificación como fallida"""
    id_notificacion: str
    detalle_error: str


class ManejadorMarcarNotificacionFallida(ComandoHandler):
    """Handler para el comando de marcar notificación como fallida"""
    
    def __init__(
        self,
        repositorio_notificaciones: RepositorioNotificaciones,
        despachador_eventos: DespachadorEventos
    ):
        self.repositorio_notificaciones = repositorio_notificaciones
        self.despachador_eventos = despachador_eventos
    
    async def handle(self, comando: ComandoMarcarNotificacionFallida) -> Notificacion:
        """Maneja el marcado de una notificación como fallida"""
        
        # Obtener la notificación
        notificacion = await self.repositorio_notificaciones.obtener_por_id(comando.id_notificacion)
        
        if not notificacion:
            raise ValueError(f"Notificación {comando.id_notificacion} no encontrada")
        
        # Marcar como fallida
        notificacion.marcar_como_fallida(comando.detalle_error)
        
        # Actualizar en el repositorio
        await self.repositorio_notificaciones.actualizar(notificacion)
        
        # Publicar eventos de dominio
        for evento in notificacion.eventos:
            await self.despachador_eventos.publicar_evento(evento)
        
        # Limpiar eventos
        notificacion.limpiar_eventos()
        
        return notificacion
