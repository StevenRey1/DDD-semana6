"""
Configuración específica para Pulsar en el microservicio de referidos.
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

    @property 
    def client_config(self) -> Dict[str, Any]:
        """Configuración del cliente Pulsar"""
        return {
            'service_url': self.service_url,
            'operation_timeout_seconds': 30,
            'connection_timeout_ms': 10000
        }

    @property
    def producer_config(self) -> Dict[str, Any]:
        """Configuración por defecto para productores"""
        return {
            'send_timeout_millis': 30000,
            'block_if_queue_full': True
        }

    @property
    def consumer_config(self) -> Dict[str, Any]:
        """Configuración por defecto para consumidores"""
        return {
            # Removidos ack_timeout_millis y read_compacted por compatibilidad
            'receiver_queue_size': 1000,
            'max_total_receiver_queue_size_across_partitions': 50000,
            'consumer_name': 'referidos-consumer'
        }

# Crear instancia global de configuración
pulsar_config = PulsarConfig()