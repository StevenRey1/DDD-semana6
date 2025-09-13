"""Fábricas para crear entidades del dominio de notificaciones"""

from typing import Dict, Any
from datetime import datetime
from .entidades import Notificacion
from .objetos_valor import TipoNotificacion, CanalNotificacion, EstadoNotificacion
from .excepciones import DatosNotificacionInvalidos


class FabricaNotificaciones:
    """Factory para crear notificaciones con validaciones de dominio"""
    
    @staticmethod
    def crear_email_bienvenida(
        id_usuario: str,
        email: str,
        nombre_usuario: str
    ) -> Notificacion:
        """Crea una notificación de bienvenida por email"""
        
        mensaje = f"¡Bienvenido {nombre_usuario}! Gracias por unirte a AlpesPartners. Estamos emocionados de tenerte con nosotros."
        
        return Notificacion.crear_notificacion(
            id_usuario=id_usuario,
            tipo="bienvenida",
            mensaje=mensaje,
            canal="email",
            destinatario=email,
            titulo=f"¡Bienvenido {nombre_usuario}!"
        )
    
    @staticmethod
    def crear_sms_codigo_verificacion(
        id_usuario: str,
        telefono: str,
        codigo: str
    ) -> Notificacion:
        """Crea una notificación SMS con código de verificación"""
        
        mensaje = f"Tu código de verificación es: {codigo}. Este código expira en 5 minutos."
        
        return Notificacion.crear_notificacion(
            id_usuario=id_usuario,
            tipo="transaccional",
            mensaje=mensaje,
            canal="sms",
            destinatario=telefono,
            titulo="Código de verificación"
        )
    
    @staticmethod
    def crear_push_promocion(
        id_usuario: str,
        device_token: str,
        titulo_promocion: str,
        descuento: int
    ) -> Notificacion:
        """Crea una notificación push promocional"""
        
        mensaje = f"¡{descuento}% de descuento en {titulo_promocion}! Aprovecha esta oferta especial."
        
        return Notificacion.crear_notificacion(
            id_usuario=id_usuario,
            tipo="promocional",
            mensaje=mensaje,
            canal="push",
            destinatario=device_token,
            titulo=f"¡{descuento}% OFF!"
        )
    
    @staticmethod
    def crear_notificacion_confirmacion(
        id_usuario: str,
        accion: str,
        canal: str = "email"
    ) -> Notificacion:
        """Crea una notificación de confirmación"""
        
        mensaje = f"Tu {accion} ha sido procesada exitosamente."
        
        return Notificacion.crear_notificacion(
            id_usuario=id_usuario,
            tipo="confirmacion",
            mensaje=mensaje,
            canal=canal
        )
    
    @staticmethod
    def crear_notificacion_alerta(
        id_usuario: str,
        descripcion_alerta: str,
        canal: str = "push"
    ) -> Notificacion:
        """Crea una notificación de alerta"""
        
        mensaje = f"Alerta: {descripcion_alerta}"
        
        return Notificacion.crear_notificacion(
            id_usuario=id_usuario,
            tipo="alerta",
            mensaje=mensaje,
            canal=canal
        )
    
    @staticmethod
    def crear_notificacion_promocion(
        id_usuario: str,
        titulo_promocion: str,
        descripcion: str,
        canal: str = "email"
    ) -> Notificacion:
        """Crea una notificación de promoción"""
        
        mensaje = f"{titulo_promocion}: {descripcion}"
        
        return Notificacion.crear_notificacion(
            id_usuario=id_usuario,
            tipo="promocion",
            mensaje=mensaje,
            canal=canal
        )
    
    @staticmethod
    def crear_notificacion_recordatorio(
        id_usuario: str,
        accion_recordar: str,
        fecha_limite: str = None,
        canal: str = "email"
    ) -> Notificacion:
        """Crea una notificación de recordatorio"""
        
        mensaje = f"Recordatorio: {accion_recordar}"
        if fecha_limite:
            mensaje += f" - Fecha límite: {fecha_limite}"
        
        return Notificacion.crear_notificacion(
            id_usuario=id_usuario,
            tipo="recordatorio",
            mensaje=mensaje,
            canal=canal
        )
    
    @staticmethod
    def crear_notificacion_sistema(
        id_usuario: str,
        mensaje_sistema: str,
        canal: str = "push"
    ) -> Notificacion:
        """Crea una notificación del sistema"""
        
        return Notificacion.crear_notificacion(
            id_usuario=id_usuario,
            tipo="sistema",
            mensaje=mensaje_sistema,
            canal=canal
        )
    
    @staticmethod
    def crear_desde_datos(datos: Dict[str, Any]) -> Notificacion:
        """Crea una notificación desde un diccionario de datos"""
        
        # Validar campos requeridos
        campos_requeridos = ["id_usuario", "tipo", "mensaje", "canal"]
        for campo in campos_requeridos:
            if campo not in datos or not datos[campo]:
                raise DatosNotificacionInvalidos(
                    campo=campo,
                    valor=str(datos.get(campo, "None")),
                    razon="Campo requerido faltante"
                )
        
        return Notificacion.crear_notificacion(
            id_usuario=datos["id_usuario"],
            tipo=datos["tipo"],
            mensaje=datos["mensaje"],
            canal=datos["canal"],
            destinatario=datos.get("destinatario"),
            titulo=datos.get("titulo")
        )
    
    @staticmethod
    def validar_datos_notificacion(datos: Dict[str, Any]) -> bool:
        """Valida que los datos para crear una notificación sean correctos"""
        
        try:
            # Validar campos requeridos
            if not datos.get("id_usuario"):
                return False
            
            if not datos.get("mensaje"):
                return False
            
            # Validar tipo y canal usando objetos valor
            TipoNotificacion(datos.get("tipo", ""))
            CanalNotificacion(datos.get("canal", ""))
            
            return True
            
        except (ValueError, TypeError):
            return False
