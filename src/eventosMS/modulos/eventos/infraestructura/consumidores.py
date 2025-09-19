from asyncio.log import logger
import pulsar, _pulsar  
import logging
import traceback
from pulsar.schema import *

from modulos.eventos.infraestructura.schema.v1.eventos import PagoCompletado, EventoCommand
from seedwork.infraestructura import utils
from seedwork.aplicacion.comandos import ejecutar_commando


def suscribirse_a_eventos_pago(app):
    """
    Consumidor del tópico eventos-pago que procesa pagos completados
    y actualiza el estado de los eventos correspondientes.
    """
    cliente = None
    try:
        # Usar configuración robusta de conexión
        pulsar_url = f'pulsar://{utils.broker_host()}:6650'
        print(f"🔗 Conectando consumidor de eventos-pago a: {pulsar_url}")
        
        cliente = pulsar.Client(
            pulsar_url,
            connection_timeout_ms=30000,
            operation_timeout_seconds=30
        )
        
        # Suscribirse sin schema para manejar JSON directamente
        consumidor = cliente.subscribe(
            'eventos-pagos', 
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name='eventos-sub-eventos-pago',
            schema=AvroSchema(PagoCompletado),
            initial_position=_pulsar.InitialPosition.Earliest
        )

        print("✅ Conectado al tópico 'eventos-pagos'")
        print("📡 Esperando eventos de pagos...")

        while True:
            try:
                mensaje = consumidor.receive(timeout_millis=5000)
                
                if mensaje:
                    print(f'📨 Evento Pago Completado recibido en servicio eventos')
                    datos = mensaje.value()
                    logger.info(f"Evento VentaReferidaConfirmada recibido: {datos}")
                    
                    # Convertir a dict para facilitar el manejo
                    datos_evento = {
                        'idPago': datos.idPago,
                        'idEvento': datos.idEvento,
                        'idSocio': datos.idSocio,
                        'monto': datos.monto,
                        'estado': datos.estado,
                        'fechaPago': datos.fechaPago                    
                    }
                    print(f"📋 Datos del evento: {datos_evento}")
                    
                    # Usar el mapeador para convertir a DTO
                    from modulos.eventos.aplicacion.mapeadores import MapeadorActualizarEventoPagoDTOJson
                    mapeador = MapeadorActualizarEventoPagoDTOJson()
                    
                    try:
                        # Convertir datos externos a DTO
                        actualizar_dto = mapeador.externo_a_dto(datos_evento)
                        
                        # Crear y ejecutar comando
                        from modulos.eventos.aplicacion.comandos.actualizar_evento_pago import ActualizarEventoPago
                        comando = ActualizarEventoPago(
                            id_evento=actualizar_dto.id_evento,
                            id_pago=actualizar_dto.id_pago,
                            estado_pago=actualizar_dto.estado_pago,
                            ganancia=actualizar_dto.ganancia,
                            fecha_pago=actualizar_dto.fecha_pago,
                            monto_pago=actualizar_dto.monto_pago
                        )
                        
                        # Ejecutar comando usando el sistema de comandos
                        print(f"Ejecutar comando: {actualizar_dto}")
                        with app.app_context():
                            ejecutar_commando(comando)
                        print(f"✅ Evento {actualizar_dto.id_evento} actualizado exitosamente")
                        
                    except Exception as e:
                        print(f"❌ Error procesando evento de pago: {e}")
                        # Log del error pero continuar procesando otros mensajes
                        logging.error(f"Error procesando evento de pago: {e}")
                    
                    # Confirmar procesamiento del mensaje
                    consumidor.acknowledge(mensaje)
                    
            except pulsar.Timeout:
                # Timeout normal, continuar escuchando
                continue
            except Exception as e:
                print(f"❌ Error recibiendo mensaje: {e}")
                logging.error(f"Error recibiendo mensaje: {e}")
                continue

    except Exception as e:
        logging.error(f'ERROR: Suscribiéndose al tópico eventos-pago: {e}')
        traceback.print_exc()
    finally:
        if cliente:
            try:
                cliente.close()
            except Exception:
                pass

def suscribirse_a_comandos_evento(app):
    """
    Consumidor del tópico eventos-pago que procesa pagos completados
    y actualiza el estado de los eventos correspondientes.
    """
    cliente = None
    try:
        # Usar configuración robusta de conexión
        pulsar_url = f'pulsar://{utils.broker_host()}:6650'
        print(f"🔗 Conectando consumidor de EventoCommand a: {pulsar_url}")
        
        cliente = pulsar.Client(
            pulsar_url,
            connection_timeout_ms=30000,
            operation_timeout_seconds=30
        )
        
        # Suscribirse sin schema para manejar JSON directamente
        consumidor = cliente.subscribe(
            'eventos-comando', 
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name='eventos-sub-comando-evento',
            schema=AvroSchema(EventoCommand),
            initial_position=_pulsar.InitialPosition.Earliest
        )

        print("✅ Conectado al tópico 'comando-evento'")
        print("📡 Esperando comandos de eventos...")

        while True:
            try:
                mensaje = consumidor.receive(timeout_millis=5000)
                
                if mensaje:
                    print('📨 EventoCommand recibido en servicio eventos')
                    datos = mensaje.value()
                    logger.info(f"EventoCommand recibido: {datos}")
                    
                    comando_tipo = datos.comando  # "Iniciar" o "Cancelar"
                    id_transaction = datos.idTransaction if hasattr(datos, 'idTransaction') else None
                    
                    # Acceder a los datos del payload
                    payload_data = datos.data
                    
                    evento_dict = {
                        'tipoEvento': payload_data.tipoEvento,
                        'idEvento': payload_data.idEvento,
                        'idReferido': payload_data.idReferido,
                        'idSocio': payload_data.idSocio,
                        'monto': payload_data.monto,
                        'fechaEvento': payload_data.fechaEvento
                    }
                    
                    print(f"📋 Comando: {comando_tipo}")
                    print(f"📋 ID Transacción: {id_transaction}")
                    print(f"📋 Datos del evento: {evento_dict}")
                    
                    # Usar el mapeador para convertir a DTO
                    from modulos.eventos.aplicacion.mapeadores import MapeadorEventoDTOJson
                    mapeador = MapeadorEventoDTOJson()
                    
                    try:
                        # Convertir datos externos a DTO
                        evento_dto = mapeador.comando_a_dto(evento_dict)
                        
                        # Crear y ejecutar comando
                        from modulos.eventos.aplicacion.comandos.crear_evento import CrearEvento
                        comando = CrearEvento(
                            tipo=evento_dto.tipo,
                            id_socio=evento_dto.id_socio,
                            id_referido=evento_dto.id_referido,
                            monto=evento_dto.monto,
                            fecha_evento=evento_dto.fecha_evento
                        )
                        
                        # Ejecutar comando usando el sistema de comandos
                        print(f"Ejecutar comando: {evento_dto}")
                        with app.app_context():
                            ejecutar_commando(comando)
                        print(f"✅ Evento {evento_dto.id_evento} actualizado exitosamente")
                        
                    except Exception as e:
                        print(f"❌ Error procesando evento de pago: {e}")
                        # Log del error pero continuar procesando otros mensajes
                        logging.error(f"Error procesando evento de pago: {e}")
                    
                    # Confirmar procesamiento del mensaje
                    consumidor.acknowledge(mensaje)
                    
            except pulsar.Timeout:
                # Timeout normal, continuar escuchando
                continue
            except Exception as e:
                print(f"❌ Error recibiendo mensaje: {e}")
                logging.error(f"Error recibiendo mensaje: {e}")
                continue

    except Exception as e:
        logging.error(f'ERROR: Suscribiéndose al tópico eventos-pago: {e}')
        traceback.print_exc()
    finally:
        if cliente:
            try:
                cliente.close()
            except Exception:
                pass