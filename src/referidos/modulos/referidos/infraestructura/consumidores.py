import pulsar, _pulsar  
import logging
import traceback
from pulsar.schema import *

from modulos.referidos.infraestructura.schema.v1.eventos import EventoRegistrado
from modulos.referidos.aplicacion.comandos.generar_referido import GenerarReferido
from seedwork.infraestructura import utils
from seedwork.aplicacion.comandos import ejecutar_commando


def suscribirse_a_eventos_tracking():
    cliente = None
    try:
        cliente = pulsar.Client(f'pulsar://{utils.broker_host()}:6650')
        consumidor = cliente.subscribe(
            'eventos-tracking', 
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name='referidos-sub-eventos-tracking',
            schema=AvroSchema(EventoRegistrado)
        )

        while True:
            mensaje = consumidor.receive()
            print(f'Evento Registrado recibido en servicio referidos: {mensaje.value().data}')
            data = mensaje.value().data

            comando = GenerarReferido(
                idSocio=data.idSocio,
                idEvento=data.idEvento,
                tipoEvento=data.tipoEvento,
                idReferido=data.idReferido,
                monto=data.monto,
                estado=data.estado,
                fechaEvento=data.fechaEvento
            )
            ejecutar_commando(comando)
            consumidor.acknowledge(mensaje)

        cliente.close()
    except:
        logging.error('ERROR: Suscribiéndose al tópico eventos-tracking!')
        traceback.print_exc()
        if cliente:
            cliente.close()