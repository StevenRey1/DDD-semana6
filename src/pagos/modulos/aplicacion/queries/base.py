from abc import ABC, abstractmethod
from typing import Any
from seedworks.aplicacion.queries import QueryHandler


class Query(ABC):
    """Clase base abstracta para todas las consultas"""
    pass


class PagoQueryBaseHandler(QueryHandler):
    """Handler base para queries de pagos"""
    
    def __init__(self):
        pass

    @abstractmethod
    def handle(self, query: Query) -> Any:
        """Maneja una consulta específica"""
        pass
