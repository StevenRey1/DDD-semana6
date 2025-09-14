"""
Comandos del módulo de Eventos
"""
from dataclasses import dataclass
from seedwork.aplicacion.comandos import Comando
from typing import Dict, Any, Optional, List


@dataclass
class CrearEvento(Comando):
    """Comando para crear un nuevo evento"""
    tipo: str
    payload: Dict[str, Any]
    metadatos: Optional[Dict[str, Any]] = None
    prioridad: str = "normal"
    correlacion_id: Optional[str] = None
    usuario_id: Optional[str] = None


@dataclass
class ProcesarEvento(Comando):
    """Comando para procesar un evento específico"""
    evento_id: str
    forzar: bool = False


@dataclass
class ReintentarEvento(Comando):
    """Comando para reintentar un evento fallido"""
    evento_id: str
    resetear_contador: bool = False


@dataclass
class ProcesarEventosLote(Comando):
    """Comando para procesar eventos en lote"""
    limite: int = 100
    tipos_incluir: Optional[List[str]] = None
    tipos_excluir: Optional[List[str]] = None
    prioridad_minima: Optional[str] = None


@dataclass
class CancelarEvento(Comando):
    """Comando para cancelar un evento"""
    evento_id: str
    motivo: str


@dataclass
class LimpiarEventosAntiguos(Comando):
    """Comando para limpiar eventos antiguos"""
    dias: int = 30
    solo_procesados: bool = True


@dataclass
class PublicarEvento(Comando):
    """Comando para publicar un evento al broker de mensajería"""
    evento_id: str
    topico: Optional[str] = None


@dataclass
class CrearEventoIntegracion(Comando):
    """Comando para crear un evento de integración"""
    origen: str
    destino: str
    tipo: str
    datos: Dict[str, Any]
    correlacion_id: Optional[str] = None
    version: str = "1.0"
    metadatos: Optional[Dict[str, Any]] = None


@dataclass
class ActualizarConfiguracionEventos(Comando):
    """Comando para actualizar la configuración del sistema de eventos"""
    max_reintentos: Optional[int] = None
    timeout_procesamiento: Optional[int] = None
    batch_size: Optional[int] = None
    intervalo_limpieza: Optional[int] = None
    dias_retencion: Optional[int] = None
    habilitar_retry_automatico: Optional[bool] = None
    habilitar_publicacion_automatica: Optional[bool] = None


@dataclass
class ReintentarEventosFallidos(Comando):
    """Comando para reintentar todos los eventos fallidos"""
    max_reintentos: int = 3
    limite: int = 100
