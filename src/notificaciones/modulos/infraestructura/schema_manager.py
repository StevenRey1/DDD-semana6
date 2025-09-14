"""
Estrategia híbrida para manejo de schemas en consumidores.
Prioridad: Schema Registry -> Schema Estático -> Schema Dinámico
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Union
from enum import Enum

import pulsar
from pulsar.schema import AvroSchema

from seedworks.infraestructura.utils import (
    obtener_schema_desde_registry, 
    validar_conexion_schema_registry
)

logger = logging.getLogger(__name__)

class EstrategiaSchema(Enum):
    """Estrategias disponibles para obtener schemas"""
    REGISTRY = "registry"
    ESTATICO = "estatico"
    DINAMICO = "dinamico"
    AUTO = "auto"

class ProveedorSchema(ABC):
    """Interfaz para proveedores de schema"""
    
    @abstractmethod
    def obtener_schema(self, topico: str) -> Optional[object]:
        """Obtiene el schema para un tópico específico"""
        pass
    
    @abstractmethod
    def deserializar_mensaje(self, mensaje) -> Dict[str, Any]:
        """Deserializa un mensaje usando el schema"""
        pass
    
    @abstractmethod
    def get_estrategia(self) -> EstrategiaSchema:
        """Retorna la estrategia utilizada"""
        pass

class ProveedorSchemaRegistry(ProveedorSchema):
    """Proveedor que usa Schema Registry"""
    
    def __init__(self, cache_schemas: bool = True):
        self.cache_schemas = cache_schemas
        self.schemas_cache = {}
        self.registry_disponible = None
    
    def _validar_registry(self) -> bool:
        """Valida si Schema Registry está disponible (con cache)"""
        if self.registry_disponible is None:
            self.registry_disponible = validar_conexion_schema_registry()
        return self.registry_disponible
    
    def obtener_schema(self, topico: str) -> Optional[AvroSchema]:
        """Obtiene schema desde Registry con cache"""
        if not self._validar_registry():
            logger.debug("❌ Schema Registry no disponible")
            return None
        
        # Verificar cache
        if self.cache_schemas and topico in self.schemas_cache:
            logger.debug(f"💾 Schema para {topico} obtenido desde cache")
            return self.schemas_cache[topico]
        
        # Obtener desde registry
        schema = obtener_schema_desde_registry(topico)
        if schema and self.cache_schemas:
            self.schemas_cache[topico] = schema
            logger.info(f"✅ Schema para {topico} cacheado")
        
        return schema
    
    def deserializar_mensaje(self, mensaje) -> Dict[str, Any]:
        """Deserializa mensaje usando schema del registry"""
        try:
            datos = mensaje.value()
            logger.debug("✅ Mensaje deserializado con Schema Registry")
            
            # Convertir a dict si es necesario
            if hasattr(datos, '__dict__'):
                return {
                    key: getattr(datos, key) 
                    for key in datos.__class__._schema.fields.keys()
                }
            return datos if isinstance(datos, dict) else {"data": datos}
            
        except Exception as e:
            logger.error(f"❌ Error deserializando con Schema Registry: {e}")
            raise
    
    def get_estrategia(self) -> EstrategiaSchema:
        return EstrategiaSchema.REGISTRY

class ProveedorSchemaEstatico(ProveedorSchema):
    """Proveedor que usa schemas estáticos predefinidos"""
    
    def __init__(self, schema_class):
        self.schema_class = schema_class
        self._schema = None
    
    def obtener_schema(self, topico: str) -> AvroSchema:
        """Retorna schema estático"""
        if not self._schema:
            self._schema = AvroSchema(self.schema_class)
        return self._schema
    
    def deserializar_mensaje(self, mensaje) -> Dict[str, Any]:
        """Deserializa usando schema estático"""
        try:
            datos = mensaje.value()
            logger.debug("✅ Mensaje deserializado con Schema Estático")
            
            # Convertir a dict si es objeto Record
            if hasattr(datos, '__dict__'):
                return {
                    key: getattr(datos, key) 
                    for key in datos.__class__._schema.fields.keys()
                }
            return datos if isinstance(datos, dict) else {"data": datos}
            
        except Exception as e:
            logger.error(f"❌ Error deserializando con Schema Estático: {e}")
            raise
    
    def get_estrategia(self) -> EstrategiaSchema:
        return EstrategiaSchema.ESTATICO

class ProveedorSchemaDinamico(ProveedorSchema):
    """Proveedor que intenta múltiples estrategias de deserialización"""
    
    def obtener_schema(self, topico: str) -> None:
        """Retorna None para que Pulsar use bytes"""
        return None
    
    def deserializar_mensaje(self, mensaje) -> Dict[str, Any]:
        """Deserializa intentando múltiples estrategias"""
        import json
        
        # Estrategia 1: Deserializar como JSON desde bytes
        try:
            raw_data = mensaje.data()
            if isinstance(raw_data, bytes):
                decoded_data = raw_data.decode('utf-8')
                datos = json.loads(decoded_data)
                logger.debug("✅ Mensaje deserializado como JSON desde bytes")
                return datos
        except Exception:
            pass
        
        # Estrategia 2: Mensaje ya deserializado
        try:
            datos = mensaje.value()
            if isinstance(datos, dict):
                logger.debug("✅ Mensaje deserializado con value()")
                return datos
        except Exception:
            pass
        
        # Estrategia 2: JSON manual
        try:
            raw_data = mensaje.data().decode('utf-8')
            datos = json.loads(raw_data)
            logger.debug("✅ Mensaje deserializado como JSON")
            return datos
        except Exception:
            pass
        
        # Estrategia 3: Datos binarios
        logger.warning("⚠️ Retornando datos binarios sin deserializar")
        return {
            'raw_data': mensaje.data().hex(),
            'size': len(mensaje.data()),
            'topic': mensaje.topic_name(),
            'message_id': str(mensaje.message_id())
        }
    
    def get_estrategia(self) -> EstrategiaSchema:
        return EstrategiaSchema.DINAMICO

class ManejadorSchemaHibrido:
    """
    Manejador que combina múltiples estrategias con fallback automático.
    
    Orden de prioridad:
    1. Schema Registry (si está disponible)
    2. Schema Estático (si se proporciona)
    3. Schema Dinámico (como último recurso)
    """
    
    def __init__(self, 
                 schema_estatico_class=None, 
                 usar_registry: bool = True,
                 usar_dinamico: bool = True):
        
        self.proveedores = []
        self.proveedor_activo = None
        
        # Configurar proveedores en orden de prioridad
        if usar_registry:
            self.proveedores.append(ProveedorSchemaRegistry())
        
        if schema_estatico_class:
            self.proveedores.append(ProveedorSchemaEstatico(schema_estatico_class))
        
        if usar_dinamico:
            self.proveedores.append(ProveedorSchemaDinamico())
    
    def obtener_schema(self, topico: str) -> Optional[object]:
        """Obtiene schema usando el primer proveedor que funcione"""
        for proveedor in self.proveedores:
            try:
                schema = proveedor.obtener_schema(topico)
                if schema:
                    self.proveedor_activo = proveedor
                    logger.info(f"✅ Schema obtenido usando estrategia: {proveedor.get_estrategia().value}")
                    return schema
            except Exception as e:
                logger.debug(f"⚠️ Proveedor {proveedor.get_estrategia().value} falló: {e}")
                continue
        
        logger.error(f"❌ No se pudo obtener schema para {topico} con ningún proveedor")
        return None
    
    def deserializar_mensaje(self, mensaje) -> Dict[str, Any]:
        """Deserializa mensaje usando el proveedor activo"""
        if not self.proveedor_activo:
            # Intentar con el primer proveedor disponible
            for proveedor in self.proveedores:
                try:
                    return proveedor.deserializar_mensaje(mensaje)
                except Exception:
                    continue
            raise ValueError("No se pudo deserializar el mensaje con ningún proveedor")
        
        return self.proveedor_activo.deserializar_mensaje(mensaje)
    
    def get_estrategia_activa(self) -> Optional[EstrategiaSchema]:
        """Retorna la estrategia actualmente en uso"""
        if self.proveedor_activo:
            return self.proveedor_activo.get_estrategia()
        return None