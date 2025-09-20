import typing
import strawberry
import uuid
import requests
import os

from datetime import datetime


AEROALPES_HOST = os.getenv("AEROALPES_ADDRESS", default="localhost")
FORMATO_FECHA = '%Y-%m-%dT%H:%M:%SZ'

def obtener_reservas(root) -> typing.List["Reserva"]:
    reservas_json = requests.get(f'http://{AEROALPES_HOST}:5000/vuelos/reserva').json()
    reservas = []

    for reserva in reservas_json:
        reservas.append(
            Reserva(
                fecha_creacion=datetime.strptime(reserva.get('fecha_creacion'), FORMATO_FECHA), 
                fecha_actualizacion=datetime.strptime(reserva.get('fecha_actualizacion'), FORMATO_FECHA), 
                id=reserva.get('id'), 
                id_usuario=reserva.get('id_usuario', '')
            )
        )

    return reservas

@strawberry.type
class Itinerario:
    # TODO Completar objeto strawberry para incluir los itinerarios
    ...

@strawberry.type
class Reserva:
    id: str
    id_usuario: str
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    #itinerarios: typing.List[Itinerario]

@strawberry.type
class ReservaRespuesta:
    mensaje: str
    codigo: int


def obtener_eventos_socio(root, id_socio: str) -> "EventosList":
    EVENTOSMS_HOST = os.getenv("EVENTOSMS_ADDRESS", default="localhost:8003")
    eventos_json = requests.get(f'http://{EVENTOSMS_HOST}:8003/eventos/{id_socio}').json()
    eventos = []

    for evento in eventos_json.get('eventos', []):
        eventos.append(
            EventoItem(
                idEvento=evento.get('idEvento'),
                idReferido=evento.get('idReferido'),
                idSocio=evento.get('idSocio', id_socio),  # Usar id_socio como fallback
                monto=evento.get('monto'),
                fechaEvento=datetime.strptime(evento.get('fechaEvento'), FORMATO_FECHA),
                estado_evento=evento.get('estado_evento'),
                ganancia=evento.get('ganancia', 0.0)
            )
        )

    return EventosList(
        idSocio=eventos_json.get('idSocio', ''),
        eventos=eventos
    )

@strawberry.type
class EventoItem:
    tipo_evento: str = "venta_creada"
    idEvento: str
    idReferido: str
    idSocio: str
    monto: float
    fechaEvento: datetime
    estado_evento: str
    ganancia: float
    

@strawberry.type
class EventosList:
    idSocio: str
    eventos: typing.List[EventoItem]

@strawberry.type
class EventoRespuesta:
    mensaje: str
    codigo: int






