from modulos.referidos.dominio.repositorio import RepositorioReferidos
from modulos.referidos.infraestructura.mapeadores import MapeadorReferido
from seedwork.aplicacion.queries import Query, QueryHandler, QueryResultado
from seedwork.aplicacion.queries import ejecutar_query as query
from dataclasses import dataclass
from .base import ReferidoQueryBaseHandler

@dataclass
class ObtenerReferidosPorSocio(Query):
    idSocio: str

class ObtenerReferidosPorSocioHandler(ReferidoQueryBaseHandler):

    def handle(self, query: ObtenerReferidosPorSocio) -> QueryResultado:
        repositorio = self.fabrica_repositorio.crear_objeto(RepositorioReferidos.__class__)
        referidos = repositorio.obtener_por_socio(query.idSocio)
        return QueryResultado(resultado=referidos)

@query.register(ObtenerReferidosPorSocio)
def ejecutar_query_obtener_referidos_por_socio(query: ObtenerReferidosPorSocio):
    handler = ObtenerReferidosPorSocioHandler()
    return handler.handle(query)