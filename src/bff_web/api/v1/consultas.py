
import strawberry
from .esquemas import *

@strawberry.type
class Query:
    eventosSocio: EventosList = strawberry.field(resolver=obtener_eventos_socio)
    referidosSocio: ReferidosList = strawberry.field(resolver=obtener_referidos_socio)
    pagoInfo: PagoInfo = strawberry.field(resolver=obtener_pago_info)