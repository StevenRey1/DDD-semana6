import time
import os
import datetime
import requests
import json
import logging
from typing import Optional, Dict, Any
from fastavro.schema import parse_schema
from pulsar.schema import *

epoch = datetime.datetime.utcfromtimestamp(0)
PULSAR_ENV: str = 'BROKER_HOST'

logger = logging.getLogger(__name__)

def time_millis():
    return int(time.time() * 1000)

def unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0

def millis_a_datetime(millis):
    return datetime.datetime.fromtimestamp(millis/1000.0)

def broker_host():
    return os.getenv(PULSAR_ENV, default="localhost")

def consultar_schema_registry(topico: str, timeout: int = 5) -> Optional[dict]:
    """
    Consulta el Schema Registry para obtener el schema de un tópico.
    
    Intenta múltiples URLs ya que diferentes versiones de Pulsar
    pueden usar rutas diferentes para el Schema Registry.
    """
    host = broker_host()
    puerto_admin = os.getenv('PULSAR_ADMIN_PORT', '8083')  # Puerto correcto para Docker
    
    # URLs alternativas para consultar schemas
    urls_posibles = [
        f'http://{host}:{puerto_admin}/admin/v2/schemas/{topico}/schema',
        f'http://{host}:{puerto_admin}/admin/v2/schemas/persistent/public/default/{topico}/schema',
        f'http://{host}:{puerto_admin}/admin/v2/persistent/public/default/{topico}/schema',
        f'http://{host}:8083/admin/v2/schemas/{topico}/schema',  # Puerto alternativo
        f'http://{host}:8083/admin/v2/schemas/persistent/public/default/{topico}/schema'
    ]
    
    for url in urls_posibles:
        try:
            logger.debug(f"🔍 Intentando obtener schema desde: {url}")
            response = requests.get(url, timeout=timeout)
            
            if response.status_code == 200:
                json_registry = response.json()
                schema_data = json_registry.get('data', json_registry)
                
                # Si data es string, parsearlo como JSON
                if isinstance(schema_data, str):
                    schema_data = json.loads(schema_data)
                
                logger.info(f"✅ Schema encontrado para {topico} en {url}")
                return schema_data
                
            elif response.status_code == 404:
                logger.debug(f"❌ Schema no encontrado en {url} (404)")
            else:
                logger.debug(f"⚠️ Error {response.status_code} en {url}")
                
        except requests.exceptions.RequestException as e:
            logger.debug(f"🔌 Error de conexión en {url}: {e}")
        except json.JSONDecodeError as e:
            logger.debug(f"📋 Error parseando JSON de {url}: {e}")
        except Exception as e:
            logger.debug(f"❓ Error inesperado en {url}: {e}")
    
    logger.warning(f"⚠️ No se pudo obtener schema para {topico} desde ninguna URL")
    return None

def obtener_schema_avro_de_diccionario(json_schema: dict) -> Optional[AvroSchema]:
    """
    Convierte un diccionario de schema JSON a AvroSchema de Pulsar.
    """
    try:
        # Si el schema viene con metadatos, extraer solo la definición
        schema_def = json_schema.get('schema', json_schema)
        if isinstance(schema_def, str):
            schema_def = json.loads(schema_def)
        
        logger.debug(f"🔄 Parseando schema: {schema_def}")
        definicion_schema = parse_schema(schema_def)
        schema = AvroSchema(None, schema_definition=definicion_schema)
        
        logger.info("✅ Schema Avro creado exitosamente")
        return schema
        
    except Exception as e:
        logger.error(f"❌ Error creando AvroSchema: {e}")
        return None

def obtener_schema_desde_registry(topico: str) -> Optional[AvroSchema]:
    """
    Función de conveniencia que combina consulta y conversión.
    """
    schema_dict = consultar_schema_registry(topico)
    if schema_dict:
        return obtener_schema_avro_de_diccionario(schema_dict)
    return None

def validar_conexion_schema_registry() -> bool:
    """
    Valida si el Schema Registry está disponible.
    """
    try:
        host = broker_host()
        puerto_admin = os.getenv('PULSAR_ADMIN_PORT', '8083')  # Puerto correcto para Docker
        
        # Probar múltiples endpoints
        urls_prueba = [
            f'http://{host}:{puerto_admin}/admin/v2/schemas',
            f'http://{host}:8083/admin/v2/schemas',  # Puerto alternativo
        ]
        
        for url in urls_prueba:
            try:
                response = requests.get(url, timeout=3)
                if response.status_code in [200, 404]:  # 404 también indica que el endpoint existe
                    logger.info(f"✅ Schema Registry está disponible en {url}")
                    return True
            except Exception:
                continue
        
        logger.warning("⚠️ Schema Registry no disponible en ninguna URL")
        return False
            
    except Exception as e:
        logger.warning(f"⚠️ Schema Registry no disponible: {e}")
        return False

