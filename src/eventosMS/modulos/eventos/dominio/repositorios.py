"""
Repositorios del dominio de Eventos
"""
from abc import ABC
from seedwork.dominio.repositorios import Repositorio

class RepositorioEventos(Repositorio, ABC):
    """Interfaz del repositorio de Eventos."""
    ...