import pulsar, _pulsar  
import logging
import traceback
from pulsar.schema import *

from modulos.referidos.infraestructura.schema.v1.eventos import EventoRegistrado
from seedwork.infraestructura import utils

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
            # Aquí se procesaría el evento EventoRegistrado
            # Por ejemplo, se podría llamar a un comando para generar un referido
            consumidor.acknowledge(mensaje)     
        cliente.close()
    except:
        logging.error('ERROR: Suscribiéndose al tópico eventos-tracking!')
        traceback.print_exc()
        if cliente:
            cliente.close()