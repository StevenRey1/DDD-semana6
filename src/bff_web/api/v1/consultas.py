
import strawberry
from .esquemas import *

@strawberry.type
class Query:
    eventos_socio: EventosList = strawberry.field(resolver=obtener_eventos_socio)