"""
Queries del módulo de Eventos
"""
from dataclasses import dataclass
from seedwork.aplicacion.queries import Query
from typing import Optional, List


@dataclass
class ObtenerEvento(Query):
    """Query para obtener un evento por ID"""
    evento_id: str


@dataclass
class ObtenerEventos(Query):
    """Query para obtener eventos con filtros"""
    tipos: Optional[List[str]] = None
    estados: Optional[List[str]] = None
    fecha_desde: Optional[str] = None
    fecha_hasta: Optional[str] = None
    correlacion_id: Optional[str] = None
    usuario_id: Optional[str] = None
    prioridad_minima: Optional[str] = None
    limite: int = 100
    offset: int = 0


@dataclass
class ObtenerEventosPorTipo(Query):
    """Query para obtener eventos de un tipo específico"""
    tipo: str
    limite: int = 100
    offset: int = 0


@dataclass
class ObtenerEventosPorEstado(Query):
    """Query para obtener eventos en un estado específico"""
    estado: str
    limite: int = 100
    offset: int = 0


@dataclass
class ObtenerEventosPendientes(Query):
    """Query para obtener eventos pendientes"""
    limite: int = 100
    prioridad_minima: Optional[str] = None


@dataclass
class ObtenerEventosFallidos(Query):
    """Query para obtener eventos fallidos"""
    max_reintentos: int = 3
    limite: int = 100


@dataclass
class ObtenerEventosCorrelacionados(Query):
    """Query para obtener eventos por ID de correlación"""
    correlacion_id: str
    limite: int = 100


@dataclass
class ObtenerEstadisticasEventos(Query):
    """Query para obtener estadísticas del sistema de eventos"""
    fecha_desde: Optional[str] = None
    fecha_hasta: Optional[str] = None


@dataclass
class ObtenerConfiguracionEventos(Query):
    """Query para obtener la configuración actual del sistema"""
    pass


@dataclass
class BuscarEventos(Query):
    """Query para búsqueda avanzada de eventos"""
    texto_busqueda: Optional[str] = None
    filtros: Optional[dict] = None
    ordenar_por: str = "fecha_creacion"
    orden_desc: bool = True
    limite: int = 100
    offset: int = 0


@dataclass
class ObtenerHistorialEvento(Query):
    """Query para obtener el historial de un evento"""
    evento_id: str


@dataclass
class ObtenerMetricasRendimiento(Query):
    """Query para obtener métricas de rendimiento"""
    fecha_desde: Optional[str] = None
    fecha_hasta: Optional[str] = None
    tipo_metrica: str = "general"  # general, por_tipo, por_estado
