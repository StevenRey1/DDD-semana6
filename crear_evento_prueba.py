#!/usr/bin/env python3
"""
Script para crear un evento de prueba en formato JSON simple
que el worker de pagos pueda procesar fácilmente.
"""

import pulsar
import json
import uuid
from datetime import datetime

def crear_evento_prueba():
    """Crea y envía un evento de prueba al tópico eventos-referido-confirmado"""
    
    # Conectar a Pulsar
    client = pulsar.Client('pulsar://localhost:6653')  # Puerto externo
    
    # Crear productor para el tópico
    producer = client.create_producer(
        topic='eventos-referido-confirmado',
        send_timeout_millis=30000
    )
    
    # Crear evento de prueba en formato JSON simple
    evento_prueba = {
        "idEvento": str(uuid.uuid4()),
        "idSocio": str(uuid.uuid4()),
        "monto": 150.75,
        "fechaEvento": datetime.utcnow().isoformat() + "Z"
    }
    
    print(f"🚀 Enviando evento de prueba: {evento_prueba}")
    
    # Enviar evento como JSON
    mensaje_json = json.dumps(evento_prueba)
    producer.send(mensaje_json.encode('utf-8'))
    
    print(f"✅ Evento enviado exitosamente al tópico eventos-referido-confirmado")
    print(f"📄 Datos enviados: {mensaje_json}")
    
    # Cerrar conexiones
    producer.close()
    client.close()

if __name__ == "__main__":
    crear_evento_prueba()