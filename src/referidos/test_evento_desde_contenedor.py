"""
Script para publicar eventos al tópico eventos-tracking desde dentro del contenedor
Simula eventos que deben ser procesados por el microservicio de referidos
"""
import pulsar
import uuid
from pulsar.schema import AvroSchema
from modulos.referidos.infraestructura.schema.v1.eventos_tracking import EventoRegistrado
from config.pulsar_config import pulsar_config

def publicar_evento_test():
    """Publica un evento de prueba al tópico eventos-tracking"""
    cliente = None
    try:
        print("📤 Conectando a Pulsar para publicar evento de prueba...")
        
        # Crear cliente
        cliente = pulsar.Client(**pulsar_config.client_config)
        
        # Crear productor
        productor = cliente.create_producer(
            'eventos-tracking',
            schema=AvroSchema(EventoRegistrado),
            **pulsar_config.producer_config
        )
        
        # Crear evento de prueba
        evento = EventoRegistrado(
            idEvento=str(uuid.uuid4()),
            tipoEvento="venta_creada",
            idReferido=str(uuid.uuid4()),
            idSocio=str(uuid.uuid4()),
            monto=299.99,
            estado="pendiente",
            fechaEvento="2025-09-13T23:20:00Z"
        )
        
        print(f"📨 Publicando evento de prueba:")
        print(f"   - idEvento: {evento.idEvento}")
        print(f"   - tipoEvento: {evento.tipoEvento}")
        print(f"   - idReferido: {evento.idReferido}")
        print(f"   - idSocio: {evento.idSocio}")
        print(f"   - monto: {evento.monto}")
        
        # Publicar evento
        productor.send(evento)
        
        print("✅ Evento publicado exitosamente al tópico eventos-tracking!")
        print("💡 El microservicio debería procesarlo y:")
        print("   1. Ejecutar GenerarReferidoCommand")
        print("   2. Persistir en BD")
        print("   3. Publicar evento de respuesta")
        
        productor.close()
        cliente.close()
        
    except Exception as e:
        print(f"❌ Error publicando evento: {e}")
        if cliente:
            cliente.close()
        raise

if __name__ == "__main__":
    print("🧪 Publicando evento de prueba al tópico eventos-tracking...")
    publicar_evento_test()
    print("🎯 Revisar logs del microservicio para ver el procesamiento")