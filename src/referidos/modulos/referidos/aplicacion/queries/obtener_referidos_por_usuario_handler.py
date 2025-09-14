from seedwork.aplicacion.queries import QueryHandler, QueryResultado
from seedwork.aplicacion.queries import ejecutar_query as query
from modulos.referidos.aplicacion.queries.obtener_referidos_por_usuario import ObtenerReferidosPorUsuario
from modulos.referidos.dominio.fabricas import FabricaReferidos
from modulos.referidos.infraestructura.fabricas import FabricaRepositorio
from modulos.referidos.infraestructura.repositorios import RepositorioReferidosPostgreSQL
from modulos.referidos.aplicacion.mapeadores import MapeadorReferidoDTOJson

class ObtenerReferidosPorUsuarioHandler(QueryHandler):
    def __init__(self):
        self._fabrica_repositorio: FabricaRepositorio = FabricaRepositorio()
        self._fabrica_referidos: FabricaReferidos = FabricaReferidos()

    @property
    def fabrica_repositorio(self):
        return self._fabrica_repositorio
    
    @property
    def fabrica_referidos(self):
        return self._fabrica_referidos

    def handle(self, query: ObtenerReferidosPorUsuario) -> QueryResultado:
        repositorio = self.fabrica_repositorio.crear_objeto(RepositorioReferidosPostgreSQL.__class__)
        referidos_infra = repositorio.obtener_por_socio_id(query.id_socio)
        
        mapeador = MapeadorReferidoDTOJson()
        referidos_externo = [mapeador.dto_a_externo(ref) for ref in referidos_infra]

        return QueryResultado(resultado={"idSocio": query.id_socio, "referidos": referidos_externo})

@query.register(ObtenerReferidosPorUsuario)
def ejecutar_query_obtener_referidos_por_usuario(query: ObtenerReferidosPorUsuario):
    handler = ObtenerReferidosPorUsuarioHandler()
    return handler.handle(query)
