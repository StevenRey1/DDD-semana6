""" Fábricas para la creación de objetos en la capa de infrastructura del dominio de vuelos

En este archivo usted encontrará las diferentes fábricas para crear
objetos complejos en la capa de infraestructura del dominio de vuelos

"""

from dataclasses import dataclass, field
from seedwork.dominio.fabricas import Fabrica
from seedwork.dominio.repositorios import Repositorio
from modulos.referidos.dominio.repositorio import RepositorioReferidos
from .repositorios import RepositorioReferidosPostgreSQL
from .excepciones import NoExisteImplementacionParaTipoFabricaExcepcion


@dataclass
class FabricaRepositorio(Fabrica):
    def crear_objeto(self, obj: type, mapeador: any = None) -> Repositorio:
        if obj == RepositorioReferidos.__class__:
            return RepositorioReferidosPostgreSQL()
        else:
            raise NoExisteImplementacionParaTipoFabricaExcepcion()