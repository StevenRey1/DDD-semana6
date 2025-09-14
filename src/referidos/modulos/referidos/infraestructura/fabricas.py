from dataclasses import dataclass
from seedwork.dominio.fabricas import Fabrica
from seedwork.dominio.repositorios import Repositorio
from modulos.referidos.dominio.repositorio import RepositorioReferidos
from modulos.referidos.infraestructura.repositorios import RepositorioReferidosPostgreSQL
from modulos.referidos.infraestructura.excepciones import NoExisteImplementacionParaTipoFabricaExcepcion

@dataclass
class FabricaRepositorio(Fabrica):
    def crear_objeto(self, obj: type, mapeador: any = None) -> Repositorio:
        if obj == RepositorioReferidos.__class__:
            return RepositorioReferidosPostgreSQL()
        else:
            raise NoExisteImplementacionParaTipoFabricaExcepcion()