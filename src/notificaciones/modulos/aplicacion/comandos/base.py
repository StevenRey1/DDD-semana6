from abc import ABC, abstractmethod
from typing import Any


class Comando(ABC):
    """Clase base abstracta para todos los comandos"""
    pass


class ComandoHandler(ABC):
    """Clase base abstracta para todos los manejadores de comandos"""
    
    @abstractmethod
    async def handle(self, comando: Comando) -> Any:
        """Maneja un comando específico de forma asíncrona"""
        pass
