"""Despachador de eventos para publicar eventos de dominio a Pulsar"""

import json
import asyncio
import logging
import time
from typing import List, Optional
import pulsar

# Import condicional de seedwork
try:
    from ....seedwork.dominio.eventos import EventoDominio
except ImportError:
    # Fallback cuando se ejecuta directamente
    from ..dominio.base_simple import EventoDominioSimple as EventoDominio

# Importar configuración de Pulsar
try:
    from ...config.pulsar_config import pulsar_config
except ImportError:
    # Fallback si no existe el archivo de configuración
    pulsar_config = None

logger = logging.getLogger(__name__)


class DespachadorEventos:
    """Despachador de eventos para el microservicio de notificaciones"""
    
    def __init__(self, pulsar_url: str = None, topic: str = None):
        # Usar configuración centralizada si está disponible
        if pulsar_config:
            self.pulsar_url = pulsar_config.service_url
            self.topic = pulsar_config.get_full_topic_name(pulsar_config.topic_eventos)
            self.config = pulsar_config
        else:
            # Fallback a configuración manual
            self.pulsar_url = pulsar_url or 'pulsar://localhost:6650'
            self.topic = topic or 'eventos-notificaciones'
            self.config = None
        
        self.client = None
        self.producer = None
        self._conectado = False
        self._retry_count = 0
        self._max_retries = pulsar_config.max_retry_attempts if pulsar_config else 5
        
    async def inicializar(self):
        """Inicializa la conexión a Pulsar"""
        if self.config:
            print("🔧 Usando configuración centralizada de Pulsar")
            self.config.print_config()
            if not self.config.validate_config():
                print("❌ Configuración de Pulsar inválida")
                return False
        
        print(f"🔌 Inicializando conexión a Pulsar...")
        print(f"   URL: {self.pulsar_url}")
        print(f"   Tópico: {self.topic}")
        
        return await self._conectar()
    
    async def _conectar(self):
        """Conecta al cliente Pulsar de forma asíncrona"""
        try:
            # Crear cliente Pulsar con parámetros válidos
            self.client = pulsar.Client(
                self.pulsar_url,
                connection_timeout_ms=30000
            )
            
            # Crear productor
            self.producer = self.client.create_producer(
                topic=self.topic,
                send_timeout_millis=30000,
                block_if_queue_full=True
            )
            
            self._conectado = True
            logger.info(f"✅ DespachadorEventos conectado a Pulsar: {self.pulsar_url}")
            print(f"✅ DespachadorEventos conectado a Pulsar: {self.pulsar_url}")
            
        except Exception as e:
            logger.error(f"❌ Error conectando DespachadorEventos a Pulsar: {e}")
            print(f"⚠️ Error conectando DespachadorEventos a Pulsar: {e}")
            self._conectado = False
    
    async def publicar_evento(self, evento: EventoDominio):
        """Publica un evento individual de forma asíncrona"""
        if not self._conectado or not self.producer:
            logger.warning("No hay conexión a Pulsar. Intentando reconectar...")
            print("⚠️ No hay conexión a Pulsar. Intentando reconectar...")
            await self._conectar()
            if not self._conectado:
                logger.error("No se pudo establecer conexión a Pulsar. Evento no publicado.")
                print("❌ No se pudo establecer conexión a Pulsar. Evento no publicado.")
                return
        
        try:
            # Crear mensaje del evento
            mensaje_evento = {
                'tipo': evento.__class__.__name__,
                'datos': evento.to_dict(),
                'timestamp': evento.fecha_evento.isoformat() if hasattr(evento, 'fecha_evento') else None
            }
            
            evento_json = json.dumps(mensaje_evento, ensure_ascii=False)
            
            # Enviar mensaje de forma síncrona para mayor confiabilidad
            msg_id = self.producer.send(evento_json.encode('utf-8'))
            
            logger.info(f"📤 Evento publicado: {evento.__class__.__name__} (ID: {msg_id})")
            print(f"📤 Evento publicado exitosamente: {evento.__class__.__name__} (ID: {msg_id})")
            
        except Exception as e:
            logger.error(f"❌ Error publicando evento {evento.__class__.__name__}: {e}")
            print(f"❌ Error publicando evento: {e}")
    
    async def publicar_eventos(self, eventos: List[EventoDominio]):
        """Publica múltiples eventos de forma asíncrona"""
        if not eventos:
            return
        
        logger.info(f"Publicando {len(eventos)} eventos...")
        
        # Publicar eventos secuencialmente para mayor confiabilidad
        for evento in eventos:
            await self.publicar_evento(evento)
    
    async def cerrar(self):
        """Cierra las conexiones de forma asíncrona"""
        try:
            if self.producer:
                self.producer.close()
                logger.info("Producer cerrado")
            if self.client:
                self.client.close()
                logger.info("Cliente Pulsar cerrado")
            self._conectado = False
            logger.info("✅ DespachadorEventos cerrado correctamente")
            print("✅ DespachadorEventos cerrado correctamente")
        except Exception as e:
            logger.error(f"⚠️ Error cerrando DespachadorEventos: {e}")
            print(f"⚠️ Error cerrando DespachadorEventos: {e}")
    
    @property
    def esta_conectado(self) -> bool:
        """Indica si el despachador está conectado"""
        return self._conectado
