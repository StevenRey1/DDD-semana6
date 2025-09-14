"""
Worker de Mensajería para el microservicio de Pagos.
Implementa el patrón Outbox y maneja la comunicación asíncrona mediante Apache Pulsar.
"""

import asyncio
import json
from datetime import datetime
from pulsar import Client
import pulsar
from pulsar.schema import AvroSchema
from .repositorio_postgresql import RepositorioPagosPG, OutboxORM
from pagos.config.pulsar_config import settings
from sqlalchemy.orm import Session

# Importar el schema para eventos de referidos confirmados
from pagos.schema.eventos_referidos import VentaReferidaConfirmada
import struct

def deserializar_avro_venta_confirmada(data_bytes):
    """
    Deserializa manualmente un mensaje Avro de VentaReferidaConfirmada.
    
    Basado en el formato observado:
    b'\x02H8ef80fee-000b-49f7-9722-b750431d11ce\x02He4cd3dc2-6741-42f5-babd-4e88652d9e6e\x02\x00PCF\x02(2025-09-14T02:17:18Z'
    
    El formato es más simple de lo que pensé. Analicemos:
    - \x02 indica que sigue un string
    - H indica que el string tiene 72 caracteres (0x48 = 72, que es exactamente la longitud de un UUID)
    - Después viene el UUID completo
    """
    try:
        pos = 0
        resultado = {}
        
        # Leer idEvento
        if data_bytes[pos] != 0x02:
            raise ValueError(f"Expected 0x02 but got {data_bytes[pos]:#x}")
        pos += 1
        
        # La longitud parece estar codificada de manera que 'H' = 72 chars
        length_byte = data_bytes[pos]
        id_evento_len = length_byte  # 'H' = 0x48 = 72
        pos += 1
        id_evento = data_bytes[pos:pos + id_evento_len].decode('utf-8')
        pos += id_evento_len
        resultado['idEvento'] = id_evento
        
        # Leer idSocio
        if pos >= len(data_bytes) or data_bytes[pos] != 0x02:
            raise ValueError(f"Expected 0x02 at pos {pos} but got {data_bytes[pos]:#x}")
        pos += 1
        
        length_byte = data_bytes[pos]
        id_socio_len = length_byte
        pos += 1
        id_socio = data_bytes[pos:pos + id_socio_len].decode('utf-8')
        pos += id_socio_len
        resultado['idSocio'] = id_socio
        
        # Leer monto (float)
        if pos >= len(data_bytes) or data_bytes[pos] != 0x02:
            raise ValueError(f"Expected 0x02 at pos {pos} but got {data_bytes[pos]:#x}")
        pos += 1
        
        # Siguiente 4 bytes son el float
        if pos + 4 > len(data_bytes):
            raise ValueError(f"Not enough bytes for float at pos {pos}")
        monto_bytes = data_bytes[pos:pos + 4]
        monto = struct.unpack('<f', monto_bytes)[0]  # little-endian float
        pos += 4
        resultado['monto'] = monto
        
        # Leer fechaEvento
        if pos >= len(data_bytes) or data_bytes[pos] != 0x02:
            raise ValueError(f"Expected 0x02 at pos {pos} but got {data_bytes[pos]:#x}")
        pos += 1
        
        length_byte = data_bytes[pos]
        fecha_len = length_byte
        pos += 1
        fecha_evento = data_bytes[pos:pos + fecha_len].decode('utf-8')
        resultado['fechaEvento'] = fecha_evento
        
        print(f"🔍 Deserialización exitosa: {resultado}")
        return resultado
        
    except Exception as e:
        print(f"❌ Error deserializando Avro manualmente: {e}")
        print(f"📊 Datos analizados - Longitud total: {len(data_bytes)}")
        if len(data_bytes) > 0:
            print(f"📊 Primeros 20 bytes: {data_bytes[:20]}")
        return None

async def despachador_outbox(repo: RepositorioPagosPG):
    """
    Implementa el patrón Outbox para garantizar la publicación confiable de eventos.
    
    Funcionamiento:
    1. Conecta con Pulsar y crea un productor para el tópico eventos-pago
    2. En un ciclo infinito:
        - Lee mensajes pendientes del outbox
        - Los publica a Pulsar
        - Marca como enviados en la misma transacción
    
    Args:
        repo: Repositorio PostgreSQL para acceder al outbox
    """
    # Inicializar cliente Pulsar y productor
    client = Client(settings.PULSAR_URL)
    producer = client.create_producer(
        topic=settings.TOPIC_PAGOS,
        batching_enabled=True,  # Habilita batch para mejor rendimiento
        block_if_queue_full=True  # Backpressure si Pulsar está sobrecargado
    )
    
    while True:
        with repo.SessionLocal() as session:
            # Obtener batch de mensajes pendientes
            outbox_items = session.query(OutboxORM).filter_by(status="PENDING").limit(settings.OUTBOX_BATCH_SIZE).all()
            
            print(f"🔄 [DESPACHADOR] Verificando outbox... Items pendientes: {len(outbox_items)}")
            
            for item in outbox_items:
                try:
                    print(f"📤 [DESPACHADOR] Publicando outbox item {item.id} al tópico {item.topic}")
                    # Publicar a Pulsar usando idPago como partition_key para ordenamiento
                    producer.send(item.payload.encode("utf-8"), partition_key=item.key)
                    # Marcar como enviado en la misma transacción
                    item.status = "SENT"
                    session.commit()
                    print(f"✅ [DESPACHADOR] Item {item.id} publicado exitosamente")
                except Exception as e:
                    print(f"❌ [DESPACHADOR] Error publicando outbox {item.id}: {e}")
                    # No hace commit - el mensaje seguirá como PENDING para reintento
        
        # Esperar antes del siguiente batch
        await asyncio.sleep(2)
    
    client.close()

def consumidor_referido(repo: RepositorioPagosPG):
    """
    Consumidor de eventos VentaReferidaConfirmada.
    
    Funcionamiento:
    1. Se suscribe al tópico eventos-referido-confirmado
    2. Al recibir un evento:
        - Si existe un pago en estado 'solicitado' → lo marca como 'completado'
        - Si no existe → crea un nuevo pago en estado 'completado'
    3. En ambos casos, publica un evento PagoCompletado vía outbox
    
    Args:
        repo: Repositorio PostgreSQL para acceder a pagos
    """
    print("🚀 [WORKER] Iniciando consumidor_referido...")
    
    try:
        # Inicializar cliente Pulsar y consumidor con schema Avro
        print("🔌 [WORKER] Conectando a Pulsar...")
        client = Client(settings.PULSAR_URL)
        print(f"✅ [WORKER] Cliente Pulsar creado exitosamente")
        
        # Crear schema Avro para VentaReferidaConfirmada
        print("📋 [WORKER] Creando schema Avro...")
        schema = AvroSchema(VentaReferidaConfirmada)
        print(f"✅ [WORKER] Schema Avro creado: {schema}")
        
        print(f"📡 [WORKER] Suscribiéndose al tópico: {settings.TOPIC_REFERIDO_CONFIRMADO}")
        consumer = client.subscribe(
            topic=settings.TOPIC_REFERIDO_CONFIRMADO,
            subscription_name="pagos-svc",
            consumer_type=pulsar.ConsumerType.Shared,  # Permite escalar horizontalmente
            schema=schema
        )
        print(f"✅ [WORKER] Suscripción exitosa con schema Avro")
        
    except Exception as e:
        print(f"❌ [WORKER] Error en inicialización: {e}")
        print(f"❌ [WORKER] Tipo de error: {type(e)}")
        import traceback
        traceback.print_exc()
        return
    
    while True:
        try:
            print("📡 Esperando mensajes en eventos-referido-confirmado...")
            # Esperar nuevo mensaje con timeout
            msg = consumer.receive(timeout_millis=5000)
            print(f"🔍 [DEBUG] Mensaje recibido: {msg is not None}")
            if msg is not None:
                print(f"🔍 [DEBUG] Mensaje válido, entrando al procesamiento")
            if msg:
                print(f"📨 Mensaje recibido con schema Avro")
                
                # Con schema Avro configurado, usar msg.value() directamente
                try:
                    data = msg.value()
                    print(f"� Datos deserializados con Avro: {data}")
                    print(f"🔍 Tipo de datos: {type(data)}")
                    
                    # Extraer campos del objeto Record deserializado
                    idEvento = data.idEvento
                    idSocio = data.idSocio
                    monto = data.monto
                    fechaEvento = data.fechaEvento
                    
                    print(f"✅ Campos extraídos - idEvento: {idEvento}, idSocio: {idSocio}, monto: {monto}, fechaEvento: {fechaEvento}")
                    
                except Exception as e:
                    print(f"❌ Error deserializando con schema Avro: {e}")
                    print(f"❌ Tipo de error: {type(e)}")
                    print(f"❌ Datos raw del mensaje: {msg.data()}")
                    # Saltar este mensaje y continuar
                    consumer.acknowledge(msg)
                    continue
            
                with repo.SessionLocal() as session:
                    # Buscar si existe un pago solicitado para este evento
                    pago_orm = session.query(repo.PagoORM).filter_by(idEvento=idEvento, estado="solicitado").first()
                    
                    if pago_orm:
                        # Actualizar pago existente
                        pago_orm.estado = "completado"
                        session.commit()
                        
                        # Preparar evento PagoCompletado
                        envelope = {
                            "meta": {
                                "event_id": pago_orm.idPago,
                                "schema_version": "v1",
                                "occurred_at": int(datetime.utcnow().timestamp()*1000),
                                "producer": settings.SERVICE_NAME,
                                "correlation_id": idEvento,
                                "causation_id": pago_orm.idPago
                            },
                            "key": pago_orm.idPago,
                            "state": {
                                "idPago": pago_orm.idPago,
                                "idEvento": pago_orm.idEvento,
                                "idSocio": pago_orm.idSocio,
                                "monto": float(pago_orm.monto),
                                "estado": "completado",
                                "fechaPago": pago_orm.fechaPago.isoformat()
                            }
                        }
                    else:
                        # Crear nuevo pago en estado completado
                        from uuid import uuid4
                        idPago = str(uuid4())
                        pago_orm = repo.PagoORM(
                            idPago=idPago,
                            idEvento=idEvento,
                            idSocio=idSocio,
                            monto=monto,
                            estado="completado",
                            fechaPago=fechaEvento
                        )
                        session.add(pago_orm)
                        session.commit()
                        
                        # Preparar evento PagoCompletado
                        envelope = {
                            "meta": {
                                "event_id": idPago,
                                "schema_version": "v1",
                                "occurred_at": int(datetime.utcnow().timestamp()*1000),
                                "producer": settings.SERVICE_NAME,
                                "correlation_id": idEvento,
                                "causation_id": idPago
                            },
                            "key": idPago,
                            "state": {
                                "idPago": idPago,
                                "idEvento": idEvento,
                                "idSocio": idSocio,
                                "monto": monto,
                                "estado": "completado",
                                "fechaPago": fechaEvento
                            }
                        }
                    
                    # Agregar evento al outbox para publicación confiable
                    print(f"💾 [CONSUMIDOR] Agregando evento al outbox - Topic: {settings.TOPIC_PAGOS}, Key: {pago_orm.idPago}")
                    repo.outbox_add(settings.TOPIC_PAGOS, pago_orm.idPago, json.dumps(envelope))
                    print(f"✅ [CONSUMIDOR] Evento agregado al outbox exitosamente")
                
                    # Confirmar procesamiento exitoso del mensaje
                    consumer.acknowledge(msg)
                    print("✅ Mensaje procesado y confirmado exitosamente!")
                
        except pulsar.Timeout:
            # Timeout esperando mensaje - continuar el loop
            print("⏱️ Timeout esperando mensajes en eventos-referido-confirmado...")
            continue
        except Exception as e:
            print(f"❌ Error procesando mensaje: {e}")
            # En caso de error, continuar el loop (no hacer acknowledge para reintento)
            continue
    
    client.close()

async def main_worker():
    """
    Función principal que ejecuta los workers en paralelo.
    
    Inicia:
    1. Despachador de outbox para publicar eventos
    2. Consumidor de eventos de ventas referidas
    """
    # Inicializar repositorio compartido
    repo = RepositorioPagosPG(settings.DB_URL)
    
    # Ejecutar despachador async y consumidor en thread separado
    import threading
    
    # Crear thread para el consumidor síncrono
    consumer_thread = threading.Thread(
        target=consumidor_referido,
        args=(repo,),
        daemon=True
    )
    consumer_thread.start()
    
    # Ejecutar despachador async en el thread principal
    await despachador_outbox(repo)

if __name__ == "__main__":
    # Punto de entrada cuando se ejecuta como script
    asyncio.run(main_worker())
