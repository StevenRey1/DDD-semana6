from abc import ABC, abstractmethod
from typing import List, Optional

from .entidades import Notificacion


class RepositorioNotificaciones(ABC):
    """Interfaz del repositorio de notificaciones siguiendo el patrón Repository"""
    
    @abstractmethod
    async def obtener_por_id(self, id_notificacion: str) -> Optional[Notificacion]:
        """Obtiene una notificación por su ID"""
        pass
    
    @abstractmethod
    async def obtener_por_usuario(self, id_usuario: str) -> List[Notificacion]:
        """Obtiene todas las notificaciones de un usuario"""
        pass
    
    @abstractmethod
    async def obtener_por_estado(self, estado: str) -> List[Notificacion]:
        """Obtiene notificaciones por estado"""
        pass
    
    @abstractmethod
    async def obtener_pendientes(self) -> List[Notificacion]:
        """Obtiene todas las notificaciones pendientes de envío"""
        pass
    
    @abstractmethod
    async def agregar(self, notificacion: Notificacion) -> None:
        """Agrega una nueva notificación"""
        pass
    
    @abstractmethod
    async def actualizar(self, notificacion: Notificacion) -> None:
        """Actualiza una notificación existente"""
        pass
    
    @abstractmethod
    async def eliminar(self, id_notificacion: str) -> None:
        """Elimina una notificación"""
        pass
    
    @abstractmethod
    async def obtener_todas(self, limite: int = 100, offset: int = 0) -> List[Notificacion]:
        """Obtiene todas las notificaciones con paginación"""
        pass
    
    @abstractmethod
    async def contar_por_usuario(self, id_usuario: str) -> int:
        """Cuenta las notificaciones de un usuario"""
        pass
