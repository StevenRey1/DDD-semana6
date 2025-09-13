"""DTOs para la capa de aplicación de notificaciones"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any


@dataclass
class NotificacionDTO:
    """DTO para transferir datos de notificación entre capas"""
    id_notificacion: str
    id_usuario: str
    tipo: str
    mensaje: str
    canal: str
    fecha_creacion: datetime
    estado: str
    fecha_envio: Optional[datetime] = None
    detalle_error: Optional[str] = None
    intentos_envio: int = 0
    destinatario: Optional[str] = None
    titulo: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el DTO a diccionario"""
        return {
            "idNotificacion": self.id_notificacion,
            "idUsuario": self.id_usuario,
            "tipo": self.tipo,
            "mensaje": self.mensaje,
            "canal": self.canal,
            "fechaCreacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            "estado": self.estado,
            "fechaEnvio": self.fecha_envio.isoformat() if self.fecha_envio else None,
            "detalleError": self.detalle_error,
            "intentosEnvio": self.intentos_envio,
            "destinatario": self.destinatario,
            "titulo": self.titulo
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NotificacionDTO':
        """Crea un DTO desde un diccionario"""
        return cls(
            id_notificacion=data["idNotificacion"],
            id_usuario=data["idUsuario"],
            tipo=data["tipo"],
            mensaje=data["mensaje"],
            canal=data["canal"],
            fecha_creacion=datetime.fromisoformat(data["fechaCreacion"]) if data.get("fechaCreacion") else datetime.utcnow(),
            estado=data["estado"],
            fecha_envio=datetime.fromisoformat(data["fechaEnvio"]) if data.get("fechaEnvio") else None,
            detalle_error=data.get("detalleError"),
            intentos_envio=data.get("intentosEnvio", 0),
            destinatario=data.get("destinatario"),
            titulo=data.get("titulo")
        )


@dataclass
class CrearNotificacionDTO:
    """DTO para solicitar la creación de una notificación"""
    id_usuario: str
    tipo: str
    mensaje: str
    canal: str
    destinatario: Optional[str] = None
    titulo: Optional[str] = None
    datos_adicionales: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "idUsuario": self.id_usuario,
            "tipo": self.tipo,
            "mensaje": self.mensaje,
            "canal": self.canal,
            "destinatario": self.destinatario,
            "titulo": self.titulo,
            "datosAdicionales": self.datos_adicionales
        }


@dataclass
class ListaNotificacionesDTO:
    """DTO para listas de notificaciones con metadatos"""
    notificaciones: List[NotificacionDTO]
    total: int
    pagina: int
    limite: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "notificaciones": [n.to_dict() for n in self.notificaciones],
            "total": self.total,
            "pagina": self.pagina,
            "limite": self.limite
        }


@dataclass
class EstadisticasNotificacionesDTO:
    """DTO para estadísticas de notificaciones"""
    total_notificaciones: int
    pendientes: int
    enviadas: int
    fallidas: int
    canceladas: int
    por_tipo: Dict[str, int]
    por_canal: Dict[str, int]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "totalNotificaciones": self.total_notificaciones,
            "pendientes": self.pendientes,
            "enviadas": self.enviadas,
            "fallidas": self.fallidas,
            "canceladas": self.canceladas,
            "porTipo": self.por_tipo,
            "porCanal": self.por_canal
        }
