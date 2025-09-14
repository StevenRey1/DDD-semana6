"""
Módulo principal de Eventos - AlpesPartners

Este módulo maneja todo el sistema de eventos del dominio, incluyendo:
- Gestión de eventos de dominio e integración
- Publicación y consumo de eventos
- Procesamiento asíncrono
- Integración con sistemas externos
"""

import logging
from typing import Dict, Any
from datetime import datetime

# Configurar logging para el módulo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def inicializar_modulo_eventos():
    """
    Inicializa el módulo completo de eventos
    """
    try:
        logger.info("Inicializando módulo de eventos...")
        
        # Registrar handlers de aplicación
        from .aplicacion.handlers import registrar_handlers
        registrar_handlers()
        
        # Inicializar consumidores
        from .infraestructura.consumidores import suscribirse_a_eventos
        consumidor = suscribirse_a_eventos()
        
        logger.info("Módulo de eventos inicializado exitosamente")
        return consumidor
        
    except Exception as e:
        logger.error(f"Error inicializando módulo de eventos: {e}")
        raise


def obtener_estadisticas_modulo() -> Dict[str, Any]:
    """
    Obtiene estadísticas generales del módulo de eventos
    """
    try:
        from .infraestructura.fabricas import obtener_fabrica_repositorio
        from .dominio.repositorios import RepositorioEventos
        from .dominio.objetos_valor import EstadoEvento
        
        fabrica = obtener_fabrica_repositorio()
        repositorio = fabrica.crear_objeto(RepositorioEventos)
        
        estadisticas = {}
        for estado in EstadoEvento:
            estadisticas[estado.valor] = repositorio.contar_por_estado(estado)
        
        estadisticas['timestamp'] = datetime.utcnow().isoformat()
        return estadisticas
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return {'error': str(e)}


def limpiar_eventos_antiguos(dias: int = 30) -> int:
    """
    Limpia eventos antiguos del sistema
    """
    try:
        from .infraestructura.fabricas import obtener_fabrica_repositorio
        from .dominio.repositorios import RepositorioEventos
        
        fabrica = obtener_fabrica_repositorio()
        repositorio = fabrica.crear_objeto(RepositorioEventos)
        
        eventos_eliminados = repositorio.limpiar_eventos_antiguos(dias)
        logger.info(f"Eventos antiguos eliminados: {eventos_eliminados}")
        
        return eventos_eliminados
        
    except Exception as e:
        logger.error(f"Error limpiando eventos antiguos: {e}")
        return 0


# Exportar clases principales para facilitar importación
from .dominio.entidades import Evento
from .dominio.objetos_valor import TipoEvento
from .dominio.fabricas import FabricaEventos
from .aplicacion.comandos import CrearEvento, ProcesarEvento
from .aplicacion.queries import ObtenerEvento, ObtenerEventos

__all__ = [
    'Evento',
    'TipoEvento', 
    'FabricaEventos',
    'CrearEvento',
    'ProcesarEvento',
    'ObtenerEvento',
    'ObtenerEventos',
    'inicializar_modulo_eventos',
    'obtener_estadisticas_modulo',
    'limpiar_eventos_antiguos'
]
