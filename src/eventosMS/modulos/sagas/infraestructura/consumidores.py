from asyncio.log import logger
import pulsar, _pulsar  
import logging
import traceback
from pulsar.schema import *

from eventosMS.modulos.sagas.infraestructura.schema.v1.eventos import EventoEventoRegistrado, IniciarSagaPago, ReferidoProcesado
from eventosMS.modulos.sagas.aplicacion.coordinadores.saga_reservas import oir_mensaje
from modulos.eventos.infraestructura.schema.v1.eventos import PagoCompletado, EventoCommand
from seedwork.infraestructura import utils
from seedwork.aplicacion.comandos import ejecutar_commando
from eventosMS.modulos.sagas.dominio.eventos.eventos import CrearEvento, EventoRegistrado


def subscribirse_a_eventos_bff(app):
    """
    Consumidor del tópico eventos-bff que procesa eventos de la BFF
    """
    cliente = None
    try:
        # Usar configuración robusta de conexión
        pulsar_url = f'pulsar://{utils.broker_host()}:6650'
        print(f"🔗 Conectando consumidor de eventos-bff a: {pulsar_url}")

        cliente = pulsar.Client(
            pulsar_url,
            connection_timeout_ms=30000,
            operation_timeout_seconds=30
        )

        # Suscribirse sin schema para manejar JSON directamente
        consumidor = cliente.subscribe(
            'comando-saga',
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name='SagaCommand',
            schema=AvroSchema(IniciarSagaPago),
            initial_position=_pulsar.InitialPosition.Earliest
        )

        print("✅ Conectado al tópico 'comando-saga'")
        print("📡 Esperando eventos de la BFF...")

        while True:
            try:
                mensaje = consumidor.receive()
                if mensaje:
                    print(f'📨 Evento BFF recibido en servicio eventos')
                    datos = mensaje.value()
                    logger.info(f"Evento BFF recibido: {datos}")
                    print(f"📋 Datos del evento: {datos}")
                    datos_dto = CrearEvento(
                        tipo=datos.data.tipoEvento ,
                        id_socio=datos.data.idSocio,
                        id_referido=datos.data.idReferido,
                        monto=datos.data.monto,
                        fecha_evento=datos.data.fechaEvento,
                        comando="Iniciar",
                        id_transaction=datos.data.idTransaction
                    )
                    
                    oir_mensaje(datos_dto)
                    
                    # acknowledge the message to remove it from the subscription
                    consumidor.acknowledge(mensaje)

            except Exception as e:
                print(f"⚠️ Error al procesar evento BFF: {e}")
                logger.error(f"Error al procesar evento BFF: {e}")
                traceback.print_exc()

    except Exception as e:
        print(f"⚠️ Error al conectar consumidor de eventos-bff: {e}")
        logger.error(f"Error al conectar consumidor de eventos-bff: {e}")
        traceback.print_exc()
    finally:
        if cliente:
            cliente.close()


def subscribirse_a_eventos_tracking(app):
    """
    Consumidor del tópico eventos-tracking que procesa eventos de eventos
    """
    cliente = None
    try:
        # Usar configuración robusta de conexión
        pulsar_url = f'pulsar://{utils.broker_host()}:6650'
        print(f"🔗 Conectando consumidor de eventos-tracking a: {pulsar_url}")

        cliente = pulsar.Client(
            pulsar_url,
            connection_timeout_ms=30000,
            operation_timeout_seconds=30
        )

        # Suscribirse sin schema para manejar JSON directamente
        consumidor = cliente.subscribe(
            'eventos-tracking',
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name='saga-eventos-tracking',
            schema=AvroSchema(EventoEventoRegistrado),
            initial_position=_pulsar.InitialPosition.Earliest
        )

        print("✅ Conectado al tópico 'eventos-tracking'")
        print("📡 Esperando eventos de eventos...")

        while True:
            try:
                mensaje = consumidor.receive()

                if mensaje:
                    print(f'📨 Evento eventos-tracking recibido en servicio saga')
                    datos = mensaje.value()
                    logger.info(f"Evento recibido: {datos}")
                    print(f"📋 Datos del evento: {datos}")
                    print(f"📋 Datos del data: {datos.data.__dict__}")
                    datos_dto = EventoRegistrado(
                        idTransaction=datos.data.idTransaction,
                        idEvento=datos.data.idEvento,
                        tipoEvento=datos.data.tipoEvento,
                        idReferido=datos.data.idReferido,
                        idSocio=datos.data.idSocio,
                        monto=datos.data.monto,
                        estado=datos.data.estado,
                        fechaEvento=datos.data.fechaEvento,
                        comando= "Iniciar" if datos.data.estado == "pendiente" else "Cancelar"
                    )         
                    oir_mensaje(datos_dto)
                    
                    # acknowledge the message to remove it from the subscription
                    consumidor.acknowledge(mensaje)

            except Exception as e:
                print(f"⚠️ Error al procesar evento tracking: {e}")
                logger.error(f"Error al procesar evento BFF: {e}")
                traceback.print_exc()

    except Exception as e:
        print(f"⚠️ Error al conectar consumidor de eventos-bff: {e}")
        logger.error(f"Error al conectar consumidor de eventos-bff: {e}")
        traceback.print_exc()
    finally:
        if cliente:
            cliente.close()
            


def subscribirse_a_evento_referido(app):
    """
    Consumidor del tópico eventos-referido que procesa eventos de eventos
    """
    cliente = None
    try:
        # Usar configuración robusta de conexión
        pulsar_url = f'pulsar://{utils.broker_host()}:6650'
        print(f"🔗 Conectando consumidor de eventos-referido a: {pulsar_url}")

        cliente = pulsar.Client(
            pulsar_url,
            connection_timeout_ms=30000,
            operation_timeout_seconds=30
        )

        # Suscribirse sin schema para manejar JSON directamente
        consumidor = cliente.subscribe(
            'eventos-referido',
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name='saga-evento-referido',
            schema=AvroSchema(ReferidoProcesado),
            initial_position=_pulsar.InitialPosition.Earliest
        )

        print("✅ Conectado al tópico 'eventos-referido'")
        print("📡 Esperando eventos de referidos...")

        while True:
            try:
                mensaje = consumidor.receive()

                if mensaje:
                    print(f'📨 Evento eventos-referido recibido en servicio saga')
                    datos = mensaje.value()
                    logger.info(f"Evento recibido: {datos}")
                    print(f"📋 Datos del evento: {datos}")
                    print(f"📋 Datos del data: {datos.data.__dict__}")
                    
                    
                    # acknowledge the message to remove it from the subscription
                    #consumidor.acknowledge(mensaje)

            except Exception as e:
                print(f"⚠️ Error al procesar eventos-referido: {e}")
                logger.error(f"Error al procesar evento-referido: {e}")
                traceback.print_exc()

    except Exception as e:
        print(f"⚠️ Error al conectar consumidor de eventos-referido: {e}")
        logger.error(f"Error al conectar consumidor de eventos-referido: {e}")
        traceback.print_exc()
    finally:
        if cliente:
            cliente.close()
            