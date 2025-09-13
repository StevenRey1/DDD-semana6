"""
Eventos de dominio para notificaciones
"""

from datetime import datetime
from typing import Optional

# Import condicional de seedwork
try:
    from .....seedwork.dominio.eventos import EventoDominio
except ImportError:
    # Fallback: crear una clase base simple
    class EventoDominio:
        def __init__(self):
            self.fecha_evento = datetime.now()
        
        def to_dict(self):
            return {
                "tipo_evento": self.__class__.__name__,
                "fecha_evento": self.fecha_evento.isoformat()
            }


class NotificacionCreada(EventoDominio):
    """Evento que se dispara cuando se crea una nueva notificación"""
    
    def __init__(self, id_notificacion: str, id_usuario: str, tipo: str, canal: str, fecha_creacion: datetime = None):
        super().__init__()
        self.id_notificacion = id_notificacion
        self.id_usuario = id_usuario
        self.tipo = tipo
        self.canal = canal
        self.fecha_creacion = fecha_creacion or datetime.now()

    def to_dict(self):
        return {
            "evento": "NotificacionCreada",
            "version": "1.0",
            "idNotificacion": self.id_notificacion,
            "idUsuario": self.id_usuario,
            "tipo": self.tipo,
            "canal": self.canal,
            "fechaCreacion": self.fecha_creacion.isoformat(),
            "fechaEvento": self.fecha_evento.isoformat()
        }


class NotificacionEnviada(EventoDominio):
    """Evento que se dispara cuando una notificación es enviada exitosamente"""
    
    def __init__(self, id_notificacion: str, id_usuario: str, fecha_envio: datetime = None):
        super().__init__()
        self.id_notificacion = id_notificacion
        self.id_usuario = id_usuario
        self.fecha_envio = fecha_envio or datetime.now()

    def to_dict(self):
        return {
            "evento": "NotificacionEnviada",
            "version": "1.0",
            "idNotificacion": self.id_notificacion,
            "idUsuario": self.id_usuario,
            "fechaEnvio": self.fecha_envio.isoformat(),
            "fechaEvento": self.fecha_evento.isoformat()
        }


class NotificacionFallida(EventoDominio):
    """Evento que se dispara cuando falla el envío de una notificación"""
    
    def __init__(self, id_notificacion: str, id_usuario: str, detalle_error: str, intentos: int, fecha_fallo: datetime = None):
        super().__init__()
        self.id_notificacion = id_notificacion
        self.id_usuario = id_usuario
        self.detalle_error = detalle_error
        self.intentos = intentos
        self.fecha_fallo = fecha_fallo or datetime.now()

    def to_dict(self):
        return {
            "evento": "NotificacionFallida",
            "version": "1.0",
            "idNotificacion": self.id_notificacion,
            "idUsuario": self.id_usuario,
            "detalleError": self.detalle_error,
            "intentos": self.intentos,
            "fechaFallo": self.fecha_fallo.isoformat(),
            "fechaEvento": self.fecha_evento.isoformat()
        }
