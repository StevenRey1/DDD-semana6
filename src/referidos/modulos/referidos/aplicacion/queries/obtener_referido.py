
from modulos.referidos.dominio.repositorio import RepositorioReferidos
from modulos.referidos.infraestructura.mapeadores import MapeadorReferido
from seedwork.aplicacion.queries import Query, QueryHandler, QueryResultado
from seedwork.aplicacion.queries import ejecutar_query as query
from dataclasses import dataclass
from .base import ReferidoQueryBaseHandler

@dataclass
class ObtenerReferido(Query):
    id: str

class ObtenerReferidoHandler(ReferidoQueryBaseHandler):

    def handle(self, query: ObtenerReferido) -> QueryResultado:
        repositorio = self.fabrica_repositorio.crear_objeto(RepositorioReferidos.__class__)
        referido =  self.fabrica_referidos.crear_objeto(repositorio.obtener_por_id(query.id), MapeadorReferido())
        return QueryResultado(resultado=referido)

@query.register(ObtenerReferido)
def ejecutar_query_obtener_referido(query: ObtenerReferido):
    handler = ObtenerReferidoHandler()
    return handler.handle(query)