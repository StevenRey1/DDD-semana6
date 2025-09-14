
from modulos.referidos.dominio.fabricas import FabricaReferidos
from modulos.referidos.infraestructura.fabricas import FabricaRepositorio
from seedwork.aplicacion.queries import QueryHandler

class ReferidoQueryBaseHandler(QueryHandler):
    def __init__(self):
        self._fabrica_repositorio: FabricaRepositorio = FabricaRepositorio()
        self._fabrica_referidos: FabricaReferidos = FabricaReferidos()

    @property
    def fabrica_repositorio(self):
        return self._fabrica_repositorio
    
    @property
    def fabrica_referidos(self):
        return self._fabrica_referidos