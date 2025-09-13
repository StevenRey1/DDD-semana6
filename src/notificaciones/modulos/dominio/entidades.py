from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import uuid
from abc import ABC

# Import condicional de seedwork
try:
    from ....seedwork.dominio.entidades import AgregacionRaiz
except ImportError:
    # Fallback cuando se ejecuta directamente
    from .base_simple import AgregacionRaizSimple as AgregacionRaiz

from .eventos.notificaciones import NotificacionCreada, NotificacionEnviada, NotificacionFallida
from .objetos_valor import TipoNotificacion, CanalNotificacion, EstadoNotificacion


@dataclass
class Notificacion(AgregacionRaiz):
    """Agregado raíz para las notificaciones"""
    
    id_notificacion: str
    id_usuario: str
    tipo: TipoNotificacion
    mensaje: str
    canal: CanalNotificacion
    fecha_creacion: datetime
    estado: EstadoNotificacion
    fecha_envio: Optional[datetime] = None
    detalle_error: Optional[str] = None
    intentos_envio: int = 0
    destinatario: Optional[str] = None
    titulo: Optional[str] = None
    
    def __post_init__(self):
        """Inicialización después de crear la instancia"""
        super().__init__()
    
    @classmethod
    def crear_notificacion(
        cls,
        id_usuario: str,
        tipo: str,
        mensaje: str,
        canal: str,
        destinatario: Optional[str] = None,
        titulo: Optional[str] = None
    ) -> 'Notificacion':
        """Factory method para crear una nueva notificación"""
        
        # Validaciones de dominio
        if not id_usuario or not id_usuario.strip():
            raise ValueError("El ID de usuario es requerido")
        
        if not mensaje or not mensaje.strip():
            raise ValueError("El mensaje es requerido")
        
        # Crear objetos valor
        tipo_notif = TipoNotificacion(tipo)
        canal_notif = CanalNotificacion(canal)
        estado_inicial = EstadoNotificacion("pendiente")
        
        # Crear la notificación
        notificacion = cls(
            id_notificacion=str(uuid.uuid4()),
            id_usuario=id_usuario.strip(),
            tipo=tipo_notif,
            mensaje=mensaje.strip(),
            canal=canal_notif,
            fecha_creacion=datetime.utcnow(),
            estado=estado_inicial,
            intentos_envio=0,
            destinatario=destinatario,
            titulo=titulo
        )
        
        # Agregar evento de dominio
        evento = NotificacionCreada(
            id_notificacion=notificacion.id_notificacion,
            id_usuario=notificacion.id_usuario,
            tipo=tipo,
            canal=canal,
            fecha_creacion=notificacion.fecha_creacion
        )
        notificacion.agregar_evento(evento)
        
        return notificacion
    
    def marcar_como_enviada(self) -> None:
        """Marca la notificación como enviada exitosamente"""
        if self.estado.valor != "pendiente":
            raise ValueError(f"No se puede enviar una notificación en estado {self.estado.valor}")
        
        self.estado = EstadoNotificacion("enviada")
        self.fecha_envio = datetime.utcnow()
        self.intentos_envio += 1
        
        # Agregar evento de dominio
        evento = NotificacionEnviada(
            id_notificacion=self.id_notificacion,
            id_usuario=self.id_usuario,
            fecha_envio=self.fecha_envio
        )
        self.agregar_evento(evento)
    
    def marcar_como_fallida(self, detalle_error: str) -> None:
        """Marca la notificación como fallida"""
        if self.estado.valor == "enviada":
            raise ValueError("No se puede marcar como fallida una notificación ya enviada")
        
        self.estado = EstadoNotificacion("fallida")
        self.detalle_error = detalle_error
        self.intentos_envio += 1
        
        # Agregar evento de dominio
        evento = NotificacionFallida(
            id_notificacion=self.id_notificacion,
            id_usuario=self.id_usuario,
            detalle_error=detalle_error,
            intentos=self.intentos_envio
        )
        self.agregar_evento(evento)
    
    def puede_reintentarse(self) -> bool:
        """Determina si la notificación puede reintentarse"""
        return (
            self.estado.valor == "fallida" and 
            self.intentos_envio < 3
        )
    
    def reintentar_envio(self) -> None:
        """Reintenta el envío de una notificación fallida"""
        if not self.puede_reintentarse():
            raise ValueError("La notificación no puede reintentarse")
        
        self.estado = EstadoNotificacion("pendiente")
        self.detalle_error = None
