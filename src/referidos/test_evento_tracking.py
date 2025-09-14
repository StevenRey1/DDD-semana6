"""
Script para probar el consumidor de EventoRegistrado
"""
import pulsar
from pulsar.schema import AvroSchema
import sys
import os

# Agregar el directorio src al path
sys.path.append('/app/src/referidos')

from modulos.referidos.infraestructura.schema.v1.eventos_tracking import EventoEventoRegistrado, EventoRegistradoPayload

def enviar_evento_registrado():
    """Enviar un evento EventoRegistrado de prueba"""
    try:
        # Conectar a Pulsar
        cliente = pulsar.Client('pulsar://pulsar:6650')
        
        # Crear el evento de prueba según la estructura correcta
        payload = EventoRegistradoPayload(
            idEvento="test-evento-123",
            tipoEvento="registroUsuario",
            idReferido="ref-456",
            idSocio="socio-789",
            monto=250.75,
            estado="activo",
            fechaEvento="2025-09-13T23:15:00Z"
        )
        
        evento = EventoEventoRegistrado(data=payload)
        
        # Crear productor para el tópico eventos-tracking
        productor = cliente.create_producer(
            'eventos-tracking',
            schema=AvroSchema(EventoEventoRegistrado)
        )
        
        print(f"📤 Enviando EventoRegistrado: {evento}")
        
        # Enviar el evento
        productor.send(evento)
        
        print("✅ Evento enviado exitosamente!")
        
        # Cerrar conexiones
        productor.close()
        cliente.close()
        
    except Exception as e:
        print(f"❌ Error enviando evento: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    enviar_evento_registrado()