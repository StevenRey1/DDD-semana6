"""Configuración del módulo de notificaciones"""

import os
from typing import Dict, Any
from dataclasses import dataclass

# Importar la configuración centralizada de Pulsar
from .pulsar_config import pulsar_config


@dataclass
class ConfiguracionNotificaciones:
    """Configuración general del módulo de notificaciones"""
    ambiente: str
    debug: bool
    log_level: str
    database_url: str
    # Configuración de Pulsar: usar pulsar_config global en lugar de dataclass
    
    # Configuraciones de canales de notificación
    email_habilitado: bool = True
    sms_habilitado: bool = True
    push_habilitado: bool = True
    
    # Límites y timeouts
    max_reintentos: int = 3
    timeout_envio: int = 30
    batch_size: int = 100


def cargar_configuracion() -> ConfiguracionNotificaciones:
    """Carga la configuración desde variables de entorno"""
    
    # Configuración general (Pulsar se maneja por separado en pulsar_config)
    return ConfiguracionNotificaciones(
        ambiente=os.getenv('AMBIENTE', 'desarrollo'),
        debug=os.getenv('DEBUG', 'true').lower() == 'true',
        log_level=os.getenv('LOG_LEVEL', 'INFO'),
        database_url=os.getenv('DATABASE_URL', 'postgresql://postgres:postgres123@localhost:5432/alpespartners'),
        email_habilitado=os.getenv('EMAIL_HABILITADO', 'true').lower() == 'true',
        sms_habilitado=os.getenv('SMS_HABILITADO', 'true').lower() == 'true',
        push_habilitado=os.getenv('PUSH_HABILITADO', 'true').lower() == 'true',
        max_reintentos=int(os.getenv('MAX_REINTENTOS', '3')),
        timeout_envio=int(os.getenv('TIMEOUT_ENVIO', '30')),
        batch_size=int(os.getenv('BATCH_SIZE', '100'))
    )


# Instancia global de configuración
configuracion = cargar_configuracion()

# Nota: Para configuración de Pulsar, usar:
# from .pulsar_config import pulsar_config
