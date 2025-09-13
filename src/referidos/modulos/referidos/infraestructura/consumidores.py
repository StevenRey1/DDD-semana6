import pulsar, _pulsar  
import logging
import traceback
from pulsar.schema import *

from modulos.referidos.infraestructura.schema.v1.eventos import EventoReferidoConfirmado, EventoReferidoCreado
from modulos.referidos.infraestructura.schema.v1.comandos import ComandoCrearReferido
from seedwork.infraestructura import utils

def suscribirse_a_comandos_eventos():
    cliente = None
    try:
        cliente = pulsar.Client(f'pulsar://{utils.broker_host()}:6650')
        consumidor = cliente.subscribe(
            'comandos-eventos', # <--- TÓPICO DE EVENTOS DE referidos
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name='referidos-sub-comandos-eventos', # Nombre único de suscripción
            schema=AvroSchema(EventoReferidoCreado) # Schema de eventos de referidos
        )

        while True:
            mensaje = consumidor.receive()
            print(f'Comando de EVENTO recibido en servicio referidos: {mensaje.value().data}')
            consumidor.acknowledge(mensaje)     
        cliente.close()
    except:
        logging.error('ERROR: Suscribiéndose al tópico de comandos-eventos de eventos - referidos!')
        traceback.print_exc()
        if cliente:
            cliente.close()

def suscribirse_a_comandos_referidos():
    cliente = None
    try:
        cliente = pulsar.Client(f'pulsar://{utils.broker_host()}:6650')
        consumidor = cliente.subscribe(
            'comandos-referidos', # <--- TÓPICO DE COMANDOS DE REFERIDOS
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name='referidos-sub-comandos-referidos', # Nombre único
            schema=AvroSchema(ComandoCrearReferido) # Schema de comandos de referidos
        )

        while True:
            mensaje = consumidor.receive()
            # Opcional: imprimir para ver que el servicio principal recibe comandos
            print(f'Comando de referidos recibido: {mensaje.value().data}')
            consumidor.acknowledge(mensaje)     
            
        cliente.close()
    except:
        logging.error('ERROR: Suscribiéndose al tópico de comandos de referidos!')
        traceback.print_exc()
        if cliente:
            cliente.close()

def suscribirse_a_eventos_referidos():
    cliente = None
    try:
        cliente = pulsar.Client(f'pulsar://{utils.broker_host()}:6650')
        consumidor = cliente.subscribe(
            'eventos-referidos', # <--- TÓPICO DE COMANDOS DE REFERIDOS
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name='referidos-sub-eventos-referidos', # Nombre único
            schema=AvroSchema(ComandoCrearReferido) # Schema de comandos de referido
        )

        while True:
            mensaje = consumidor.receive()
            # Opcional: imprimir para ver que el servicio principal recibe comandos
            print(f'evento de referidos recibido: {mensaje.value().data}')
            consumidor.acknowledge(mensaje)     
            
        cliente.close()
    except:
        logging.error('ERROR: Suscribiéndose al tópico de eventos de referidos!')
        traceback.print_exc()
        if cliente:
            cliente.close()