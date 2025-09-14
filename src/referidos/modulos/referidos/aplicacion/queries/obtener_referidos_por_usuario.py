from seedwork.aplicacion.queries import Query, QueryHandler, QueryResultado
from seedwork.aplicacion.queries import ejecutar_query as query
from dataclasses import dataclass

@dataclass
class ObtenerReferidosPorUsuario(Query):
    id_socio: str

class ObtenerReferidosPorUsuarioHandler(QueryHandler):
    def handle(self, query: ObtenerReferidosPorUsuario) -> QueryResultado:
        # Implementar lógica para obtener referidos por usuario
        # Por ahora, se retorna un resultado mock
        mock_referidos = [
            {
                "idEvento": "uuid-evento-1",
                "idReferido": "uuid-referido-1",
                "tipoEvento": "venta_creada",
                "monto": 150.50,
                "estado": "pendiente",
                "fechaEvento": "2025-09-09T20:00:00Z",
            }
        ]
        return QueryResultado(resultado={"idSocio": query.id_socio, "referidos": mock_referidos})

@query.register(ObtenerReferidosPorUsuario)
def ejecutar_query_obtener_referidos_por_usuario(query: ObtenerReferidosPorUsuario):
    handler = ObtenerReferidosPorUsuarioHandler()
    return handler.handle(query)
