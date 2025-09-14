#!/usr/bin/env python3
"""
Script para enviar un evento de prueba al tópico eventos-tracking
con el schema correcto de EventoRegistrado
"""

import sys
import os

# Determinar la ruta base dependiendo de dónde se ejecute el script
if os.path.basename(os.getcwd()) == 'referidos':
    # Ejecutado desde src/referidos/
    sys.path.append('.')
    sys.path.append('../..')
else:
    # Ejecutado desde la raíz del proyecto
    sys.path.append(os.path.join('src', 'referidos'))

import pulsar
from pulsar.schema import AvroSchema

# Importar el schema
from modulos.referidos.infraestructura.schema.v1.eventos_tracking import EventoRegistrado
from config.pulsar_config import pulsar_config

def enviar_evento_prueba():
    """Envía un evento de prueba al tópico eventos-tracking"""
    cliente = None
    try:
        # Configuración específica para el host local (puerto expuesto de Docker Compose integrado)
        # Crear cliente de Pulsar con configuración simplificada
        cliente = pulsar.Client('pulsar://localhost:6653')
        
        # Crear productor con el schema correcto
        productor = cliente.create_producer(
            topic='eventos-tracking',
            schema=AvroSchema(EventoRegistrado)
        )
        
        # Crear evento de prueba
        evento = EventoRegistrado(
            idEvento="550e8400-e29b-41d4-a716-446655440001",
            tipoEvento="venta_creada",
            idReferido="550e8400-e29b-41d4-a716-446655440002", 
            idSocio="550e8400-e29b-41d4-a716-446655440003",
            monto=299.99,
            estado="pendiente",
            fechaEvento="2025-09-13T23:55:00Z"
        )
        
        # Enviar evento
        productor.send(evento)
        print(f"✅ Evento enviado exitosamente: {evento}")
        
        productor.close()
        cliente.close()
        
    except Exception as e:
        print(f"❌ Error enviando evento: {str(e)}")
        import traceback
        traceback.print_exc()
        if cliente:
            cliente.close()

if __name__ == "__main__":
    enviar_evento_prueba()