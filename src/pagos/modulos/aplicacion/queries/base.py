from abc import ABC, abstractmethod
from typing import Any


class Query(ABC):
    """Clase base abstracta para todas las consultas"""
    pass


class QueryHandler(ABC):
    """Clase base abstracta para todos los manejadores de consultas"""
    
    @abstractmethod
    async def handle(self, query: Query) -> Any:
        """Maneja una consulta específica de forma asíncrona"""
        pass
