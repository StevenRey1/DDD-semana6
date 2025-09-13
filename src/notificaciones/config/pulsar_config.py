"""
Configuración específica para Pulsar en el microservicio de notificaciones.
"""
import os
from typing import Dict, Any


class PulsarConfig:
    """Configuración centralizada para Apache Pulsar"""
    
    def __init__(self):
        # Configuración básica de conexión
        # Detectar si estamos en Docker o local
        pulsar_host = os.getenv('PULSAR_HOST', 'localhost')
        pulsar_port = os.getenv('PULSAR_PORT', '6650')
        
        # Si hay PULSAR_URL, usarla directamente
        if os.getenv('PULSAR_URL'):
            self.service_url = os.getenv('PULSAR_URL')
        else:
            self.service_url = f'pulsar://{pulsar_host}:{pulsar_port}'
        
        # Admin URL
        admin_host = os.getenv('PULSAR_ADMIN_HOST', pulsar_host) 
        admin_port = os.getenv('PULSAR_ADMIN_PORT', '8080')
        if os.getenv('PULSAR_ADMIN_URL'):
            self.admin_url = os.getenv('PULSAR_ADMIN_URL')
        else:
            # Para admin, si estamos en Docker usar nombre del servicio, si no localhost
            if pulsar_host == 'pulsar':  # Docker
                self.admin_url = f'http://pulsar:{admin_port}'
            else:  # Local
                self.admin_url = f'http://localhost:{admin_port}'
        
        # Configuración de tenant/namespace
        self.tenant = os.getenv('PULSAR_TENANT', 'public')
        self.namespace = os.getenv('PULSAR_NAMESPACE', 'default')
        
        # Configuración de tópicos
        self.topic_eventos = os.getenv('PULSAR_TOPIC_EVENTOS', 'eventos-dominio')
        self.topic_notificaciones = os.getenv('PULSAR_TOPIC_NOTIFICACIONES', 'notificaciones')
        
        # Configuración de subscripciones
        self.subscription_name = os.getenv('PULSAR_SUBSCRIPTION', 'notificaciones-sub')
        
        # Configuración del producer
        self.producer_timeout_ms = int(os.getenv('PULSAR_PRODUCER_TIMEOUT_MS', '10000'))
        self.producer_batch_size = int(os.getenv('PULSAR_PRODUCER_BATCH_SIZE', '100'))
        
        # Configuración del consumer
        self.consumer_timeout_ms = int(os.getenv('PULSAR_CONSUMER_TIMEOUT_MS', '5000'))
        
        # Configuración de reconexión
        self.max_retry_attempts = int(os.getenv('PULSAR_MAX_RETRY_ATTEMPTS', '5'))
        self.retry_delay_seconds = int(os.getenv('PULSAR_RETRY_DELAY_SECONDS', '2'))
        
        # Configuración de autenticación (opcional)
        self.auth_plugin = os.getenv('PULSAR_AUTH_PLUGIN')
        self.auth_params = os.getenv('PULSAR_AUTH_PARAMS')
        
        # Configuración TLS (opcional)
        self.use_tls = os.getenv('PULSAR_USE_TLS', 'false').lower() == 'true'
        self.tls_trust_certs = os.getenv('PULSAR_TLS_TRUST_CERTS')
        self.tls_cert_file = os.getenv('PULSAR_TLS_CERT_FILE')
        self.tls_key_file = os.getenv('PULSAR_TLS_KEY_FILE')
    
    def get_full_topic_name(self, topic_name: str) -> str:
        """Construye el nombre completo del tópico"""
        return f"persistent://{self.tenant}/{self.namespace}/{topic_name}"
    
    def get_producer_config(self) -> Dict[str, Any]:
        """Configuración para el producer"""
        config = {
            'topic': self.get_full_topic_name(self.topic_eventos),
            'send_timeout_millis': self.producer_timeout_ms,
            'batching_enabled': True,
            'batching_max_messages': self.producer_batch_size,
            'block_if_queue_full': True,
        }
        
        return config
    
    def get_consumer_config(self, topic_name: str = None) -> Dict[str, Any]:
        """Configuración para el consumer"""
        topic = topic_name or self.topic_notificaciones
        
        config = {
            'topic': self.get_full_topic_name(topic),
            'subscription_name': self.subscription_name,
            'consumer_type': 'Shared',  # Permite múltiples consumers
            'initial_position': 'Latest',
            'receiver_queue_size': 1000,
        }
        
        return config
    
    def get_client_config(self) -> Dict[str, Any]:
        """Configuración para el cliente Pulsar"""
        config = {
            'service_url': self.service_url,
            'connection_timeout_ms': 10000,
        }
        
        # Agregar autenticación si está configurada
        if self.auth_plugin and self.auth_params:
            config['authentication'] = {
                'auth_plugin': self.auth_plugin,
                'auth_params': self.auth_params
            }
        
        # Agregar configuración TLS si está habilitada
        if self.use_tls:
            config['use_tls'] = True
            if self.tls_trust_certs:
                config['tls_trust_certs_file_path'] = self.tls_trust_certs
            if self.tls_cert_file and self.tls_key_file:
                config['tls_certificate_file_path'] = self.tls_cert_file
                config['tls_private_key_file_path'] = self.tls_key_file
        
        return config
    
    def validate_config(self) -> bool:
        """Valida que la configuración esté completa"""
        required_fields = [
            self.service_url,
            self.tenant,
            self.namespace,
            self.topic_eventos,
            self.subscription_name
        ]
        
        missing_fields = [field for field in required_fields if not field]
        
        if missing_fields:
            print(f"❌ Faltan campos de configuración obligatorios: {missing_fields}")
            return False
        
        print("✅ Configuración de Pulsar validada correctamente")
        return True
    
    def print_config(self):
        """Imprime la configuración actual (sin datos sensibles)"""
        print("\n🔧 Configuración de Pulsar:")
        print(f"  - Service URL: {self.service_url}")
        print(f"  - Admin URL: {self.admin_url}")
        print(f"  - Tenant: {self.tenant}")
        print(f"  - Namespace: {self.namespace}")
        print(f"  - Tópico eventos: {self.get_full_topic_name(self.topic_eventos)}")
        print(f"  - Tópico notificaciones: {self.get_full_topic_name(self.topic_notificaciones)}")
        print(f"  - Subscription: {self.subscription_name}")
        print(f"  - Producer timeout: {self.producer_timeout_ms}ms")
        print(f"  - Consumer timeout: {self.consumer_timeout_ms}ms")
        print(f"  - Max retry attempts: {self.max_retry_attempts}")
        print(f"  - Use TLS: {self.use_tls}")
        print(f"  - Auth plugin: {'Configurado' if self.auth_plugin else 'No configurado'}")
    
    def get_legacy_config(self) -> Dict[str, Any]:
        """Método para compatibilidad con código legacy que esperaba ConfiguracionPulsar"""
        return {
            'url_servicio': self.service_url,
            'timeout_conexion': self.consumer_timeout_ms // 1000,
            'tenant': self.tenant,
            'namespace': self.namespace,
            'topico_eventos': self.topic_eventos,
            'suscripcion': self.subscription_name
        }


# Instancia global de configuración
pulsar_config = PulsarConfig()
