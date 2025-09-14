"""
🎯 SCRIPT MAESTRO PARA VERIFICAR PUBLICACIÓN DE EVENTOS
=====================================================

Este script realiza las siguientes pruebas:
1. Inicia consumidores en background para VentaReferidaConfirmada y VentaReferidaRechazada
2. Publica eventos de prueba 
3. Verifica que los eventos se reciben correctamente
4. Muestra estadísticas finales

¡Perfecto para verificar que todo funciona! 😄
"""

import pulsar
from pulsar.schema import AvroSchema
import _pulsar
import sys
import threading
import time
import signal

sys.path.append('/app/src/referidos')

from modulos.referidos.infraestructura.schema.v1.eventos_tracking import VentaReferidaConfirmada, VentaReferidaRechazada
from modulos.referidos.infraestructura.publicadores import PublicadorEventosReferido
from config.pulsar_config import pulsar_config

# Variables globales para estadísticas
eventos_confirmados_recibidos = 0
eventos_rechazados_recibidos = 0
running = True

def signal_handler(sig, frame):
    global running
    print("\n🛑 Deteniendo pruebas...")
    running = False

def consumidor_confirmados():
    """Consumidor para eventos VentaReferidaConfirmada"""
    global eventos_confirmados_recibidos, running
    cliente = None
    
    try:
        print("🟢 [CONFIRMADOS] Iniciando consumidor...")
        cliente = pulsar.Client(**pulsar_config.client_config)
        
        consumidor = cliente.subscribe(
            'eventos-referido-confirmado',
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name='test-verificacion-confirmado',
            schema=AvroSchema(VentaReferidaConfirmada),
            **pulsar_config.consumer_config
        )
        
        print("🟢 [CONFIRMADOS] ✅ Listo para recibir eventos!")
        
        while running:
            try:
                mensaje = consumidor.receive(timeout_millis=1000)
                evento = mensaje.value()
                eventos_confirmados_recibidos += 1
                
                print("🎉 [CONFIRMADOS] Evento recibido!")
                print(f"   📋 ID Evento: {evento.idEvento}")
                print(f"   👤 ID Socio: {evento.idSocio}")
                print(f"   💰 Monto: ${evento.monto}")
                print(f"   📅 Fecha: {evento.fechaEvento}")
                print(f"   📊 Total recibidos: {eventos_confirmados_recibidos}")
                print("   " + "="*50)
                
                consumidor.acknowledge(mensaje)
                
            except Exception as e:
                if "TimeOut" not in str(e) and running:
                    print(f"🟢 [CONFIRMADOS] ⚠️ Error: {e}")
        
        print("🟢 [CONFIRMADOS] 🔒 Cerrando consumidor...")
        cliente.close()
        
    except Exception as e:
        print(f"🟢 [CONFIRMADOS] ❌ Error crítico: {e}")
        if cliente:
            cliente.close()

def consumidor_rechazados():
    """Consumidor para eventos VentaReferidaRechazada"""
    global eventos_rechazados_recibidos, running
    cliente = None
    
    try:
        print("🔴 [RECHAZADOS] Iniciando consumidor...")
        cliente = pulsar.Client(**pulsar_config.client_config)
        
        consumidor = cliente.subscribe(
            'eventos-referido-rechazado',
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name='test-verificacion-rechazado',
            schema=AvroSchema(VentaReferidaRechazada),
            **pulsar_config.consumer_config
        )
        
        print("🔴 [RECHAZADOS] ✅ Listo para recibir eventos!")
        
        while running:
            try:
                mensaje = consumidor.receive(timeout_millis=1000)
                evento = mensaje.value()
                eventos_rechazados_recibidos += 1
                
                print("💥 [RECHAZADOS] Evento recibido!")
                print(f"   📋 ID Evento: {evento.idEvento}")
                print(f"   👤 ID Socio: {evento.idSocio}")
                print(f"   💰 Monto: ${evento.monto}")
                print(f"   ❌ Razón: {evento.razon}")
                print(f"   📅 Fecha: {evento.fechaEvento}")
                print(f"   📊 Total recibidos: {eventos_rechazados_recibidos}")
                print("   " + "="*50)
                
                consumidor.acknowledge(mensaje)
                
            except Exception as e:
                if "TimeOut" not in str(e) and running:
                    print(f"🔴 [RECHAZADOS] ⚠️ Error: {e}")
        
        print("🔴 [RECHAZADOS] 🔒 Cerrando consumidor...")
        cliente.close()
        
    except Exception as e:
        print(f"🔴 [RECHAZADOS] ❌ Error crítico: {e}")
        if cliente:
            cliente.close()

def publicar_eventos_prueba():
    """Publica eventos de prueba"""
    print("📤 [PUBLICADOR] Iniciando publicación de eventos de prueba...")
    
    try:
        publicador = PublicadorEventosReferido()
        
        # Publicar 3 eventos confirmados
        for i in range(1, 4):
            datos_confirmacion = {
                "idEvento": f"test-conf-{i}-{int(time.time())}",
                "idSocio": f"socio-test-{i}", 
                "monto": 100.0 + i * 50,
                "fechaEvento": "2025-09-13T23:30:00Z"
            }
            
            print(f"📤 [PUBLICADOR] Publicando VentaReferidaConfirmada #{i}...")
            publicador.publicar_venta_confirmada(datos_confirmacion)
            time.sleep(2)
        
        # Publicar 2 eventos rechazados
        for i in range(1, 3):
            datos_rechazo = {
                "idEvento": f"test-rech-{i}-{int(time.time())}",
                "idSocio": f"socio-test-{i}",
                "monto": 200.0 + i * 25,
                "razon": f"Motivo de prueba #{i}",
                "fechaEvento": "2025-09-13T23:30:00Z"
            }
            
            print(f"📤 [PUBLICADOR] Publicando VentaReferidaRechazada #{i}...")
            publicador.publicar_venta_rechazada(datos_rechazo)
            time.sleep(2)
            
        print("📤 [PUBLICADOR] ✅ Todos los eventos de prueba publicados!")
        
    except Exception as e:
        print(f"📤 [PUBLICADOR] ❌ Error publicando: {e}")

def main():
    global running
    print("🚀 INICIANDO VERIFICACIÓN DE EVENTOS DE REFERIDOS")
    print("=" * 60)
    print("⏰ Duración de la prueba: 45 segundos")
    print("📊 Eventos a publicar: 3 confirmados + 2 rechazados")
    print("=" * 60)
    
    # Configurar signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Iniciar consumidores en threads separados
    thread_confirmados = threading.Thread(target=consumidor_confirmados, daemon=True)
    thread_rechazados = threading.Thread(target=consumidor_rechazados, daemon=True)
    
    thread_confirmados.start()
    time.sleep(1)
    thread_rechazados.start()
    time.sleep(3)  # Dar tiempo a que se conecten
    
    # Publicar eventos de prueba
    thread_publicador = threading.Thread(target=publicar_eventos_prueba, daemon=True)
    thread_publicador.start()
    
    # Esperar 45 segundos para que lleguen todos los eventos
    try:
        time.sleep(45)
    except KeyboardInterrupt:
        pass
    
    # Detener todo
    running = False
    
    # Esperar un poco para que los threads terminen
    time.sleep(2)
    
    # Mostrar estadísticas finales
    print("\n" + "="*60)
    print("📊 ESTADÍSTICAS FINALES")
    print("="*60)
    print(f"✅ Eventos VentaReferidaConfirmada recibidos: {eventos_confirmados_recibidos}")
    print(f"❌ Eventos VentaReferidaRechazada recibidos: {eventos_rechazados_recibidos}")
    print(f"📈 Total de eventos procesados: {eventos_confirmados_recibidos + eventos_rechazados_recibidos}")
    
    if eventos_confirmados_recibidos >= 3 and eventos_rechazados_recibidos >= 2:
        print("🎉 ¡PRUEBA EXITOSA! Todos los eventos se publicaron y recibieron correctamente!")
    else:
        print("⚠️ Algunos eventos no se recibieron. Puede ser problema de timing o configuración.")
    
    print("="*60)
    print("🏁 Verificación completada!")

if __name__ == "__main__":
    main()