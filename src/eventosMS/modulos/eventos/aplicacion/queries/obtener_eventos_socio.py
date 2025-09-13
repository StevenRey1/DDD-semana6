# Propósito: Define la consulta ObtenerPago y su handler para recuperar un pago por su ID.

from uuid import UUID
from modulos.eventos.dominio.repositorios import RepositorioEventos
from modulos.eventos.infraestructura.mapeadores import MapeadorEvento
from seedwork.aplicacion.queries import Query, QueryResultado
from seedwork.aplicacion.queries import ejecutar_query as query
from dataclasses import dataclass
from .base import EventoQueryBaseHandler

@dataclass
class ObtenerEventosSocio(Query):
    id_socio: str

class ObtenerEventosSocioHandler(EventoQueryBaseHandler):

    def handle(self, query: ObtenerEventosSocio) -> QueryResultado:
        socio_uuid = UUID(query.id_socio)
        repositorio = self.fabrica_repositorio.crear_objeto(RepositorioEventos.__class__)
        eventos =  self.fabrica_eventos.crear_lista_eventos(repositorio.obtener_por_id_socio(socio_uuid), MapeadorEvento())
        return QueryResultado(resultado=eventos)

@query.register(ObtenerEventosSocio)
def ejecutar_query_obtener_eventos_socio(query: ObtenerEventosSocio):
    handler = ObtenerEventosSocioHandler()
    return handler.handle(query)