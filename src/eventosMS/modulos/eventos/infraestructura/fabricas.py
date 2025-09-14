"""
Fábricas de infraestructura para el módulo de Eventos
"""
from dataclasses import dataclass
from seedwork.dominio.fabricas import Fabrica
from seedwork.dominio.repositorios import Repositorio
from modulos.eventos.dominio.repositorios import RepositorioEventos
from .repositorios import RepositorioEventosPostgreSQL
from .excepciones import NoExisteImplementacionParaTipoFabricaExcepcion


@dataclass
class FabricaRepositorio(Fabrica):
    """
    Fábrica para crear repositorios de eventos
    """

    def crear_objeto(self, obj: type, mapeador: any = None) -> Repositorio:
        if obj == RepositorioEventos.__class__:
            return RepositorioEventosPostgreSQL()
        else:
            raise NoExisteImplementacionParaTipoFabricaExcepcion()



