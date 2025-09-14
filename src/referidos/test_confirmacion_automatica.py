#!/usr/bin/env python3
"""
Script para probar la confirmación automática de referidos
Este script:
1. Publica un evento al tópico eventos-tracking
2. Verifica que el microservicio procese el evento
3. Verifica que se publique automáticamente la confirmación en eventos-referido-confirmado
"""

import pulsar
from pulsar.schema import AvroSchema
from modulos.referidos.infraestructura.schema.v1.eventos_tracking import EventoRegistrado
import uuid
import time
import threading

def publicar_evento_tracking():
    """Publica un evento de tracking para testing"""
    try:
        print("🧪 Publicando evento de prueba al tópico eventos-tracking...")
        
        # Configurar cliente Pulsar
        client = pulsar.Client('pulsar://localhost:6650')
        
        # Crear productor para eventos-tracking
        producer = client.create_producer(
            'eventos-tracking',
            schema=AvroSchema(EventoRegistrado)
        )
        
        # Crear evento de prueba
        evento_test = EventoRegistrado(
            idEvento=str(uuid.uuid4()),
            idSocio="test-socio-" + str(uuid.uuid4()),
            idReferido="test-referido-" + str(uuid.uuid4()),
            monto=199.99,
            estado="pendiente",
            fechaEvento="2025-09-13T23:50:00Z",
            tipoEvento="venta_creada"
        )
        
        print(f"📤 Enviando evento: {evento_test}")
        
        # Publicar evento
        producer.send(evento_test)
        print("✅ Evento publicado exitosamente!")
        
        # Cerrar conexiones
        producer.close()
        client.close()
        
        return evento_test
        
    except Exception as e:
        print(f"❌ Error publicando evento: {e}")
        raise e

def monitorear_confirmacion():
    """Monitorea el tópico eventos-referido-confirmado para verificar la confirmación automática"""
    try:
        print("👀 Monitoreando tópico eventos-referido-confirmado...")
        
        # Configurar cliente Pulsar
        client = pulsar.Client('pulsar://localhost:6650')
        
        # Schema para eventos de confirmación (importar desde schema)
        from modulos.referidos.infraestructura.schema.v1.eventos_tracking import VentaReferidaConfirmada
        
        # Crear consumidor para eventos-referido-confirmado
        consumer = client.subscribe(
            'eventos-referido-confirmado',
            subscription_name='test-monitor-confirmacion',
            schema=AvroSchema(VentaReferidaConfirmada),
            consumer_type=pulsar.ConsumerType.Shared
        )
        
        print("✅ Consumidor iniciado. Esperando confirmaciones...")
        
        # Escuchar por 30 segundos
        timeout = time.time() + 30
        while time.time() < timeout:
            try:
                msg = consumer.receive(timeout_millis=5000)
                confirmacion = msg.value()
                print(f"🎉 ¡CONFIRMACIÓN RECIBIDA! {confirmacion}")
                consumer.acknowledge(msg)
                break
            except:
                print("⏳ Esperando confirmación...")
                continue
        
        # Cerrar conexiones
        consumer.close()
        client.close()
        
    except Exception as e:
        print(f"❌ Error monitoreando confirmaciones: {e}")

def main():
    """Función principal del test"""
    print("🚀 Iniciando test de confirmación automática...")
    print("=" * 60)
    
    # Iniciar monitor en thread separado
    monitor_thread = threading.Thread(target=monitorear_confirmacion)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # Esperar un poco para que se inicie el monitor
    time.sleep(2)
    
    # Publicar evento de tracking
    evento = publicar_evento_tracking()
    
    print("=" * 60)
    print("✅ Test completado. Revisa los logs del microservicio y el monitor.")
    print(f"Evento enviado: ID={evento.idEvento}, Socio={evento.idSocio}, Referido={evento.idReferido}")
    
    # Esperar para que termine el monitor
    time.sleep(35)

if __name__ == "__main__":
    main()