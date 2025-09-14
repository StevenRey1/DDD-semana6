"""
Estrategia híbrida para schemas en notificaciones:
- Schemas estáticos para eventos críticos
- Schemas dinámicos para eventos genéricos
"""

from abc import ABC, abstractmethod
import json
import logging
from typing import Optional, Dict, Any, Union

import pulsar
from pulsar.schema import AvroSchema, AutoConsumeSchema

logger = logging.getLogger(__name__)

class EstrategiaSchema(ABC):
    """Estrategia base para manejo de schemas"""
    
    @abstractmethod
    def obtener_schema(self) -> Optional[object]:
        """Retorna el schema a usar"""
        pass
    
    @abstractmethod
    def deserializar_mensaje(self, mensaje) -> Dict[str, Any]:
        """Deserializa el mensaje según la estrategia"""
        pass


class SchemaEstatico(EstrategiaSchema):
    """Estrategia con schema Avro predefinido"""
    
    def __init__(self, schema_class):
        self.schema_class = schema_class
    
    def obtener_schema(self) -> AvroSchema:
        return AvroSchema(self.schema_class)
    
    def deserializar_mensaje(self, mensaje) -> Dict[str, Any]:
        """Deserializa usando schema Avro"""
        try:
            datos = mensaje.value()
            logger.info(f"✅ Deserializado con schema estático: {type(datos)}")
            
            # Convertir a dict si es objeto Record
            if hasattr(datos, '__dict__'):
                return {
                    key: getattr(datos, key) 
                    for key in datos.__class__._schema.fields.keys()
                }
            return datos
            
        except Exception as e:
            logger.error(f"❌ Error deserializando con schema estático: {e}")
            raise


class SchemaDinamico(EstrategiaSchema):
    """Estrategia con auto-detección de schema"""
    
    def obtener_schema(self) -> AutoConsumeSchema:
        return AutoConsumeSchema()
    
    def deserializar_mensaje(self, mensaje) -> Dict[str, Any]:
        """Deserializa intentando múltiples estrategias"""
        # Estrategia 1: Auto-schema de Pulsar
        try:
            datos = mensaje.value()
            if isinstance(datos, dict):
                logger.info("✅ Deserializado con auto-schema")
                return datos
        except Exception as e:
            logger.debug(f"Auto-schema falló: {e}")
        
        # Estrategia 2: JSON manual
        try:
            raw_data = mensaje.data().decode('utf-8')
            datos = json.loads(raw_data)
            logger.info("✅ Deserializado como JSON")
            return datos
        except Exception as e:
            logger.debug(f"JSON falló: {e}")
        
        # Estrategia 3: Datos binarios
        logger.warning("⚠️ Retornando datos binarios sin deserializar")
        return {
            'raw_data': mensaje.data().hex(),
            'size': len(mensaje.data()),
            'topic': mensaje.topic_name()
        }


class SchemaHibrido(EstrategiaSchema):
    """Estrategia híbrida que combina estático y dinámico"""
    
    def __init__(self, schema_class=None, fallback_dinamico=True):
        self.schema_estatico = SchemaEstatico(schema_class) if schema_class else None
        self.schema_dinamico = SchemaDinamico() if fallback_dinamico else None
    
    def obtener_schema(self) -> Optional[object]:
        # Prioridad al schema estático si existe
        if self.schema_estatico:
            return self.schema_estatico.obtener_schema()
        elif self.schema_dinamico:
            return self.schema_dinamico.obtener_schema()
        return None
    
    def deserializar_mensaje(self, mensaje) -> Dict[str, Any]:
        """Intenta estático primero, luego dinámico"""
        if self.schema_estatico:
            try:
                return self.schema_estatico.deserializar_mensaje(mensaje)
            except Exception as e:
                logger.warning(f"Schema estático falló: {e}")
        
        if self.schema_dinamico:
            return self.schema_dinamico.deserializar_mensaje(mensaje)
        
        raise ValueError("No hay estrategia de schema disponible")


# Ejemplo de uso en consumidores
class ConsumidorConEstrategiaSchema:
    """Ejemplo de consumidor usando estrategias de schema"""
    
    def __init__(self, topico: str, estrategia: EstrategiaSchema):
        self.topico = topico
        self.estrategia = estrategia
    
    def crear_consumidor(self):
        """Crea consumidor usando la estrategia de schema"""
        cliente = pulsar.Client('pulsar://localhost:6650')
        
        schema = self.estrategia.obtener_schema()
        consumidor = cliente.subscribe(
            self.topico,
            subscription_name=f'consumer-{self.topico}',
            schema=schema
        )
        return consumidor
    
    async def procesar_mensaje(self, mensaje):
        """Procesa mensaje usando la estrategia"""
        try:
            datos = self.estrategia.deserializar_mensaje(mensaje)
            logger.info(f"📨 Mensaje procesado: {datos}")
            return datos
        except Exception as e:
            logger.error(f"❌ Error procesando mensaje: {e}")
            raise


if __name__ == "__main__":
    # Ejemplo de uso
    from schema.eventos_referidos import VentaReferidaConfirmada
    
    # Para eventos críticos - schema estático
    estrategia_referidos = SchemaEstatico(VentaReferidaConfirmada)
    
    # Para eventos genéricos - schema dinámico  
    estrategia_sistema = SchemaDinamico()
    
    # Para eventos mixtos - híbrido
    estrategia_hibrida = SchemaHibrido(
        schema_class=VentaReferidaConfirmada,
        fallback_dinamico=True
    )