"""
Consumidor de prueba para verificar que los eventos VentaReferidaConfirmada 
y VentaReferidaRechazada se publican correctamente en sus tópicos
"""
import pulsar
from pulsar.schema import AvroSchema
import _pulsar
import sys
import threading
import time

sys.path.append('/app/src/referidos')

from modulos.referidos.infraestructura.schema.v1.eventos_tracking import VentaReferidaConfirmada, VentaReferidaRechazada
from config.pulsar_config import pulsar_config

def consumir_venta_confirmada():
    """Consumidor para eventos VentaReferidaConfirmada"""
    cliente = None
    try:
        print("🔄 Iniciando consumidor para eventos-referido-confirmado...")
        cliente = pulsar.Client(**pulsar_config.client_config)
        
        consumidor = cliente.subscribe(
            'eventos-referido-confirmado',
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name='test-sub-confirmado',
            schema=AvroSchema(VentaReferidaConfirmada),
            **pulsar_config.consumer_config
        )
        
        print("✅ Consumidor de VentaReferidaConfirmada listo. Esperando mensajes...")
        
        # Escuchar por 30 segundos
        timeout_time = time.time() + 30
        while time.time() < timeout_time:
            try:
                mensaje = consumidor.receive(timeout_millis=1000)
                evento = mensaje.value()
                print(f"📨 VentaReferidaConfirmada recibida:")
                print(f"   - idEvento: {evento.idEvento}")
                print(f"   - idSocio: {evento.idSocio}")
                print(f"   - monto: {evento.monto}")
                print(f"   - fechaEvento: {evento.fechaEvento}")
                print("   ✅ Evento procesado correctamente!")
                print("-" * 50)
                consumidor.acknowledge(mensaje)
            except Exception as e:
                if "TimeOut" not in str(e):
                    print(f"⚠️ Error procesando mensaje: {e}")
                # Continue listening
        
        print("⏰ Timeout alcanzado para consumidor de VentaReferidaConfirmada")
        cliente.close()
        
    except Exception as e:
        print(f"❌ Error en consumidor VentaReferidaConfirmada: {e}")
        if cliente:
            cliente.close()

def consumir_venta_rechazada():
    """Consumidor para eventos VentaReferidaRechazada"""
    cliente = None
    try:
        print("🔄 Iniciando consumidor para eventos-referido-rechazado...")
        cliente = pulsar.Client(**pulsar_config.client_config)
        
        consumidor = cliente.subscribe(
            'eventos-referido-rechazado',
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name='test-sub-rechazado',
            schema=AvroSchema(VentaReferidaRechazada),
            **pulsar_config.consumer_config
        )
        
        print("✅ Consumidor de VentaReferidaRechazada listo. Esperando mensajes...")
        
        # Escuchar por 30 segundos
        timeout_time = time.time() + 30
        while time.time() < timeout_time:
            try:
                mensaje = consumidor.receive(timeout_millis=1000)
                evento = mensaje.value()
                print(f"📨 VentaReferidaRechazada recibida:")
                print(f"   - idEvento: {evento.idEvento}")
                print(f"   - idSocio: {evento.idSocio}")
                print(f"   - monto: {evento.monto}")
                print(f"   - razon: {evento.razon}")
                print(f"   - fechaEvento: {evento.fechaEvento}")
                print("   ✅ Evento procesado correctamente!")
                print("-" * 50)
                consumidor.acknowledge(mensaje)
            except Exception as e:
                if "TimeOut" not in str(e):
                    print(f"⚠️ Error procesando mensaje: {e}")
                # Continue listening
        
        print("⏰ Timeout alcanzado para consumidor de VentaReferidaRechazada")
        cliente.close()
        
    except Exception as e:
        print(f"❌ Error en consumidor VentaReferidaRechazada: {e}")
        if cliente:
            cliente.close()

def main():
    print("🎯 Iniciando consumidores de prueba para eventos de referidos...")
    print("=" * 70)
    
    # Crear threads para ambos consumidores
    thread_confirmado = threading.Thread(target=consumir_venta_confirmada)
    thread_rechazado = threading.Thread(target=consumir_venta_rechazada)
    
    # Iniciar threads
    thread_confirmado.start()
    time.sleep(1)  # Pequeña pausa entre inicios
    thread_rechazado.start()
    
    # Esperar que terminen
    thread_confirmado.join()
    thread_rechazado.join()
    
    print("=" * 70)
    print("🏁 Consumidores de prueba finalizados")

if __name__ == "__main__":
    main()