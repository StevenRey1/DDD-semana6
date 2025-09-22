import pulsar
from pulsar.schema import *
import json
import datetime

# Importamos TODOS los eventos y payloads que este despachador puede manejar
from modulos.eventos.infraestructura.schema.v1.eventos import (
    EventoEventoRegistrado, EventoRegistradoPayload
)
# Importamos los eventos de DOMINIO para poder identificarlos
from modulos.eventos.dominio.eventos import EventoRegistrado

from seedwork.infraestructura import utils

epoch = datetime.datetime.utcfromtimestamp(0)

def unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0

class Despachador:
    def _publicar_mensaje(self, mensaje, topico):
        cliente = pulsar.Client(f'pulsar://{utils.broker_host()}:6650')
        # Obtenemos el schema del propio objeto del mensaje
        publicador = cliente.create_producer(topico, schema=AvroSchema(EventoEventoRegistrado))
        publicador.send(mensaje)
        cliente.close()

    def publicar_evento(self, evento, topico):
        print('===================================================================')
        print(f'¡DESPACHADOR: Publicando evento en el tópico {topico}! ID: {evento.evento_id}')
        print('===================================================================')
        # =======================================
        # Determinamos el tipo de evento de dominio para saber qué payload crear
        print(f"Evento: {evento}")
        print(f"Evento: {evento.__dict__}")

        if isinstance(evento, EventoRegistrado):
            payload = EventoRegistradoPayload(
                idTransaction=evento.id_transaction,
                idEvento=str(evento.evento_id),
                tipoEvento=str(evento.tipo_evento),
                idReferido=str(evento.id_referido),
                idSocio=str(evento.id_socio),
                monto=float(evento.monto),
                estado=str(evento.estado),
                fechaEvento=str(evento.fecha_evento)
            )
            print(f"Payload: {payload.__dict__}")
            evento_integracion = EventoEventoRegistrado(data=payload)
        else:
            # Si no reconocemos el evento, no hacemos nada.
            # Podríamos también lanzar un error.
            return

        # Publicamos el evento de integración que acabamos de crear
        self._publicar_mensaje(evento_integracion, topico)