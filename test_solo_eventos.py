#!/usr/bin/env python3
"""
Test simple para probar solo eventosMS
"""
import requests
import json
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_solo_eventos():
    """Test para registrar un evento en eventosMS"""
    
    # Datos del evento
    payload = {
        "tipoEvento": "venta_creada",
        "idReferido": "c2036830-03e5-4c4b-98a0-782798e9688f",
        "idSocio": "1dea7b8e-c788-4354-972f-fc0b346fe49e",
        "monto": 125000.0,
        "fechaEvento": "2025-09-14T01:30:00Z"
    }
    
    logging.info("🧪 === PROBANDO SOLO eventoMS ===")
    logging.info(f"📤 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        # Registrar evento
        response = requests.post(
            'http://localhost:8003/eventos',
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200 or response.status_code == 201:
            logging.info("✅ Evento registrado exitosamente!")
            logging.info(f"📋 Respuesta: {response.text}")
        else:
            logging.error(f"❌ Error registrando evento: {response.status_code} - {response.text}")
            
    except Exception as e:
        logging.error(f"❌ Error conectando con eventosMS: {e}")

if __name__ == "__main__":
    test_solo_eventos()