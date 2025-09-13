"""Implementación del repositorio de notificaciones"""

from typing import List, Optional
import asyncio
import logging

from ..dominio.repositorios import RepositorioNotificaciones
from ..dominio.entidades import Notificacion

logger = logging.getLogger(__name__)


class RepositorioNotificacionesMemoria(RepositorioNotificaciones):
    """Implementación en memoria del repositorio de notificaciones"""
    
    def __init__(self):
        self.notificaciones: List[Notificacion] = []
        self._lock = asyncio.Lock()
    
    async def obtener_por_id(self, id_notificacion: str) -> Optional[Notificacion]:
        """Obtiene una notificación por su ID de forma asíncrona"""
        async with self._lock:
            for notificacion in self.notificaciones:
                if notificacion.id_notificacion == id_notificacion:
                    return notificacion
            return None
    
    async def obtener_por_usuario(self, id_usuario: str, limite: int = None, offset: int = 0) -> List[Notificacion]:
        """Obtiene notificaciones de un usuario con paginación opcional"""
        async with self._lock:
            notificaciones_usuario = [
                notif for notif in self.notificaciones 
                if notif.id_usuario == id_usuario
            ]
            
            if limite is None:
                return notificaciones_usuario[offset:]
            else:
                return notificaciones_usuario[offset:offset + limite]
    
    async def obtener_por_estado(self, estado: str) -> List[Notificacion]:
        """Obtiene notificaciones por estado de forma asíncrona"""
        async with self._lock:
            return [
                notif for notif in self.notificaciones 
                if notif.estado.valor == estado
            ]
    
    async def obtener_pendientes(self) -> List[Notificacion]:
        """Obtiene todas las notificaciones pendientes de forma asíncrona"""
        return await self.obtener_por_estado("pendiente")
    
    async def agregar(self, notificacion: Notificacion) -> None:
        """Agrega una nueva notificación de forma asíncrona"""
        async with self._lock:
            self.notificaciones.append(notificacion)
            logger.info(f"📝 Notificación agregada al repositorio: {notificacion.id_notificacion} (Total: {len(self.notificaciones)})")
    
    async def actualizar(self, notificacion: Notificacion) -> None:
        """Actualiza una notificación existente de forma asíncrona"""
        async with self._lock:
            for i, notif in enumerate(self.notificaciones):
                if notif.id_notificacion == notificacion.id_notificacion:
                    self.notificaciones[i] = notificacion
                    return
            
            # Si no se encuentra, la agregamos (upsert)
            self.notificaciones.append(notificacion)
    
    async def eliminar(self, id_notificacion: str) -> None:
        """Elimina una notificación de forma asíncrona"""
        async with self._lock:
            self.notificaciones = [
                notif for notif in self.notificaciones 
                if notif.id_notificacion != id_notificacion
            ]
    
    async def obtener_todas(self, limite: int = 100, offset: int = 0) -> List[Notificacion]:
        """Obtiene todas las notificaciones con paginación de forma asíncrona"""
        async with self._lock:
            logger.info(f"📊 Obteniendo todas las notificaciones: Total en repositorio = {len(self.notificaciones)}")
            return self.notificaciones[offset:offset + limite]
    
    async def contar_por_usuario(self, id_usuario: str) -> int:
        """Cuenta las notificaciones de un usuario de forma asíncrona"""
        async with self._lock:
            return len([
                notif for notif in self.notificaciones 
                if notif.id_usuario == id_usuario
            ])
    
    async def contar_total(self) -> int:
        """Cuenta el total de notificaciones de forma asíncrona"""
        async with self._lock:
            return len(self.notificaciones)
    
    async def limpiar(self) -> None:
        """Limpia todas las notificaciones (útil para testing)"""
        async with self._lock:
            self.notificaciones.clear()
