from modulos.referidos.dominio.excepciones import TipoObjetoNoExisteEnDominioReferidosExcepcion
from seedwork.dominio.repositorios import Mapeador
from seedwork.dominio.fabricas import Fabrica
from modulos.referidos.dominio.entidades import Referido
from seedwork.dominio.entidades import Entidad
from dataclasses import dataclass
from seedwork.dominio.repositorios import Repositorio


@dataclass
class _FabricaReferido(Fabrica):
    def crear_objeto(self, obj, mapeador: Mapeador) -> Referido:
        if isinstance(obj, Entidad):
            print(obj)
            return mapeador.entidad_a_dto(obj)
        else:
            referido: Referido = mapeador.dto_a_entidad(obj)
            return referido

@dataclass
class FabricaReferidos(Fabrica):
    def crear_objeto(self, obj: any, mapeador: Mapeador) -> any:
        if mapeador.obtener_tipo() == Referido.__class__:
            fabrica_referido = _FabricaReferido()
            return fabrica_referido.crear_objeto(obj, mapeador)
        else:
            raise TipoObjetoNoExisteEnDominioReferidosExcepcion()