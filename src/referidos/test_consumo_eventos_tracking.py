"""
Script para probar el consumo del tópico eventos-tracking
Publica eventos al tópico y verifica que el microservicio los procese
"""
import sys
sys.path.append('/app/src/referidos')

import pulsar
from pulsar.schema import AvroSchema
from modulos.referidos.infraestructura.schema.v1.eventos_tracking import EventoRegistrado
from config.pulsar_config import pulsar_config
import uuid
import time

def publicar_evento_tracking(tipo_evento="venta_creada"):
    """
    Publica un evento de prueba al tópico eventos-tracking
    """
    cliente = None
    try:
        print(f"📤 Publicando EventoRegistrado de tipo '{tipo_evento}' al tópico eventos-tracking...")
        
        # Crear cliente Pulsar
        cliente = pulsar.Client(**pulsar_config.client_config)
        
        # Crear productor para eventos-tracking
        productor = cliente.create_producer(
            'eventos-tracking',
            schema=AvroSchema(EventoRegistrado),
            **pulsar_config.producer_config
        )
        
        # Crear evento de prueba
        evento = EventoRegistrado(
            idEvento=str(uuid.uuid4()),
            tipoEvento=tipo_evento,
            idReferido=str(uuid.uuid4()),
            idSocio=str(uuid.uuid4()),
            monto=125.75,
            estado="pendiente",
            fechaEvento="2025-09-13T23:30:00Z"
        )
        
        # Publicar evento
        productor.send(evento)
        
        print(f"✅ EventoRegistrado publicado exitosamente!")
        print(f"   - idEvento: {evento.idEvento}")
        print(f"   - tipoEvento: {evento.tipoEvento}")
        print(f"   - idReferido: {evento.idReferido}")
        print(f"   - idSocio: {evento.idSocio}")
        print(f"   - monto: {evento.monto}")
        print(f"   - estado: {evento.estado}")
        
        productor.close()
        cliente.close()
        
        return evento
        
    except Exception as e:
        print(f"❌ Error publicando evento: {e}")
        if cliente:
            cliente.close()
        raise e

def verificar_procesamiento():
    """
    Verifica que el consumidor procese eventos correctamente
    """
    print("🧪 Iniciando prueba de procesamiento de eventos-tracking...")
    print("=" * 60)
    
    # Publicar diferentes tipos de eventos
    tipos_evento = ['venta_creada', 'registroUsuario', 'compra']
    
    for tipo in tipos_evento:
        print(f"\n📌 Probando evento tipo: {tipo}")
        print("-" * 40)
        
        try:
            evento = publicar_evento_tracking(tipo)
            print(f"⏳ Esperando 3 segundos para que el consumidor procese...")
            time.sleep(3)
            
            print(f"💡 Si el microservicio está corriendo, debería haber procesado el evento {evento.idEvento}")
            print(f"   Revisar logs del contenedor para confirmar que se ejecutó GenerarReferidoCommand")
            
        except Exception as e:
            print(f"❌ Error en tipo {tipo}: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Prueba completada!")
    print("💡 Para verificar que los eventos se procesaron:")
    print("   1. Revisar logs del contenedor: docker logs referidos-service")
    print("   2. Verificar registros en BD: GET /referidos/{idSocio}")
    print("   3. Verificar eventos publicados a respuesta")

def main():
    """Función principal"""
    print("🚀 Script de verificación de consumo de eventos-tracking")
    print("🎯 Este script publica eventos al tópico eventos-tracking")
    print("📊 El microservicio debería consumirlos y generar referidos")
    print("")
    
    try:
        verificar_procesamiento()
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    main()