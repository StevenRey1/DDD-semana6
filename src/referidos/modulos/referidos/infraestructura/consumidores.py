import pulsar, _pulsar  
import logging
import traceback
import json
from pulsar.schema import *

from modulos.referidos.infraestructura.schema.v1.eventos import EventoReferidoConfirmado, EventoReferidoCreado
from modulos.referidos.infraestructura.schema.v1.eventos_tracking import EventoRegistrado
from modulos.referidos.infraestructura.schema.v1.comandos import ComandoCrearReferido
from modulos.referidos.aplicacion.comandos.generar_referido import GenerarReferidoCommand
from seedwork.infraestructura import utils
from seedwork.aplicacion.comandos import ejecutar_commando

# Importar configuración de Pulsar
from config.pulsar_config import pulsar_config

def suscribirse_a_eventos_tracking():
    """
    Consumidor principal: Escucha EventoRegistrado del tópico eventos-tracking
    Según especificación del Microservicio 2: Seguimiento de Referidos
    """
    cliente = None
    try:
        cliente = pulsar.Client(**pulsar_config.client_config)
        consumidor = cliente.subscribe(
            'eventos-tracking',  # Tópico según especificación
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name='referidos-sub-eventos-tracking',
            schema=AvroSchema(EventoRegistrado),
            receiver_queue_size=1000,
            max_total_receiver_queue_size_across_partitions=50000,
            consumer_name='referidos-consumer'
        )

        print("🔄 Consumidor de eventos-tracking iniciado para referidos")
        
        while True:
            mensaje = consumidor.receive()
            try:
                evento_data = mensaje.value()
                print(f"📨 EventoRegistrado recibido: {evento_data}")
                
                # Filtrar solo eventos de tipo registroUsuario o compra según especificación
                if evento_data.data.tipoEvento in ['registroUsuario', 'compra', 'venta_creada']:
                    # Crear comando para generar referido
                    comando = GenerarReferidoCommand(
                        idEvento=evento_data.data.idEvento,
                        tipoEvento=evento_data.data.tipoEvento,
                        idReferido=evento_data.data.idReferido,
                        idSocio=evento_data.data.idSocio,
                        monto=evento_data.data.monto,
                        estado=evento_data.data.estado,
                        fechaEvento=evento_data.data.fechaEvento
                    )
                    
                    # Ejecutar comando
                    ejecutar_commando(comando)
                    print(f"✅ Referido generado para evento: {evento_data.data.idEvento}")
                    
                consumidor.acknowledge(mensaje)
                
            except Exception as e:
                print(f"❌ Error procesando evento: {str(e)}")
                traceback.print_exc()
                consumidor.acknowledge(mensaje)  # Acknowledge para evitar reintento infinito
                
        cliente.close()
    except Exception as e:
        logging.error('ERROR: Suscribiéndose al tópico eventos-tracking')
        traceback.print_exc()
        if cliente:
            cliente.close()

def suscribirse_a_comandos_eventos():
    """
    Consumidor legacy: mantiene compatibilidad con comandos-eventos
    """
    cliente = None
    try:
        cliente = pulsar.Client(**pulsar_config.client_config)
        consumidor = cliente.subscribe(
            'comandos-eventos',
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name='referidos-sub-comandos-eventos',
            schema=AvroSchema(EventoReferidoCreado),
            receiver_queue_size=1000,
            max_total_receiver_queue_size_across_partitions=50000,
            consumer_name='referidos-consumer'
        )

        while True:
            mensaje = consumidor.receive()
            print(f'📜 Comando de EVENTO legacy recibido: {mensaje.value().data}')
            consumidor.acknowledge(mensaje)     
        cliente.close()
    except:
        logging.error('ERROR: Suscribiéndose al tópico comandos-eventos legacy')
        traceback.print_exc()
        if cliente:
            cliente.close()

def suscribirse_a_comandos_referidos():
    """
    Consumidor legacy: mantiene compatibilidad con comandos-referidos
    """
    cliente = None
    try:
        cliente = pulsar.Client(**pulsar_config.client_config)
        consumidor = cliente.subscribe(
            'comandos-referidos',
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name='referidos-sub-comandos-referidos',
            schema=AvroSchema(ComandoCrearReferido),
            receiver_queue_size=1000,
            max_total_receiver_queue_size_across_partitions=50000,
            consumer_name='referidos-consumer'
        )

        while True:
            mensaje = consumidor.receive()
            print(f'📜 Comando de referidos legacy recibido: {mensaje.value().data}')
            consumidor.acknowledge(mensaje)     
            
        cliente.close()
    except:
        logging.error('ERROR: Suscribiéndose al tópico comandos-referidos legacy')
        traceback.print_exc()
        if cliente:
            cliente.close()
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