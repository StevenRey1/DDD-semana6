import pulsar
from pulsar.schema import *
import json
import datetime

# Importamos TODOS los eventos y payloads que este despachador puede manejar
from modulos.sagas.infraestructura.schema.v1.comandos import (
    EventoCommand, EventoCommandPayload, ReferidoCommandPayload, ReferidoCommand
)
# Importamos los eventos de DOMINIO para poder identificarlos

from seedwork.infraestructura import utils

epoch = datetime.datetime.utcfromtimestamp(0)

def unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0

class Despachador:
    def _publicar_mensaje(self, mensaje, topico):
        cliente = pulsar.Client(f'pulsar://{utils.broker_host()}:6650')
        # Obtenemos el schema del propio objeto del mensaje
        publicador = cliente.create_producer(topico, schema=AvroSchema(EventoCommand))
        publicador.send(mensaje)
        cliente.close()

    def publicar_evento_command(self, mensaje: dict):
        print('===================================================================')
        print(f'¡SAGA-DESPACHADOR: Publicando evento en el tópico {"eventos-comando"}! ID: {mensaje}')
        print('===================================================================')
        # =======================================
        # Determinamos el tipo de evento de dominio para saber qué payload crear
        payload = EventoCommandPayload(
                idEvento=str(mensaje.get('idEvento')),
                tipoEvento=str(mensaje.get('tipoEvento')),
                idReferido=str(mensaje.get('idReferido')),
                idSocio=str(mensaje.get('idSocio')),
                monto=float(mensaje.get('monto', 0)),
                fechaEvento=str(mensaje.get('fechaEvento'))
            )
        evento_integracion = EventoCommand(
                idTransaction=str(mensaje.get('idTransaction')),
                comando=str(mensaje.get('comando')),
                data=payload)

        # Publicamos el evento de integración que acabamos de crear
        self._publicar_mensaje(evento_integracion, 'eventos-comando')

    def publicar_referido_command(self, mensaje: dict):
        print('===================================================================')
        print(f'¡SAGA-DESPACHADOR: Publicando evento en el tópico {"referido-comando"}! ID: {mensaje}')
        print('===================================================================')
        # =======================================
        # Determinamos el tipo de evento de dominio para sabe   r qué payload crear
        print(mensaje)
        payload = ReferidoCommandPayload(
                idSocio=str(mensaje.get('idSocio')),
                idReferido=str(mensaje.get('idReferido')),
                idEvento=str(mensaje.get('idEvento')),
                monto=float(mensaje.get('monto', 0)),
                estado=str(mensaje.get('estado')),
                fechaEvento=str(mensaje.get('fechaEvento')),
                tipoEvento=str(mensaje.get('tipoEvento'))
        )

        evento_integracion = ReferidoCommand(
            idTransaction = str(mensaje.get('idTransaction')),
            comando = str(mensaje.get('comando')),
            data = payload
        )

        # Publicamos el evento de integración que acabamos de crear
        self._publicar_mensaje(evento_integracion, 'comando-referido')