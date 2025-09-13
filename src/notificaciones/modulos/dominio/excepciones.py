"""Excepciones específicas del dominio de notificaciones"""


class NotificacionException(Exception):
    """Excepción base para el dominio de notificaciones"""
    pass


class NotificacionNoEncontrada(NotificacionException):
    """Excepción cuando no se encuentra una notificación"""
    
    def __init__(self, id_notificacion: str):
        self.id_notificacion = id_notificacion
        super().__init__(f"Notificación con ID {id_notificacion} no encontrada")


class EstadoNotificacionInvalido(NotificacionException):
    """Excepción cuando se intenta realizar una operación con estado inválido"""
    
    def __init__(self, estado_actual: str, operacion: str):
        self.estado_actual = estado_actual
        self.operacion = operacion
        super().__init__(f"No se puede {operacion} una notificación en estado {estado_actual}")


class TipoNotificacionInvalido(NotificacionException):
    """Excepción cuando se especifica un tipo de notificación inválido"""
    
    def __init__(self, tipo: str, tipos_validos: list):
        self.tipo = tipo
        self.tipos_validos = tipos_validos
        super().__init__(f"Tipo de notificación '{tipo}' inválido. Tipos válidos: {tipos_validos}")


class CanalNotificacionInvalido(NotificacionException):
    """Excepción cuando se especifica un canal de notificación inválido"""
    
    def __init__(self, canal: str, canales_validos: list):
        self.canal = canal
        self.canales_validos = canales_validos
        super().__init__(f"Canal de notificación '{canal}' inválido. Canales válidos: {canales_validos}")


class LimiteReintentosAlcanzado(NotificacionException):
    """Excepción cuando se alcanza el límite máximo de reintentos"""
    
    def __init__(self, id_notificacion: str, intentos: int):
        self.id_notificacion = id_notificacion
        self.intentos = intentos
        super().__init__(f"Límite de reintentos alcanzado para notificación {id_notificacion}: {intentos} intentos")


class DatosNotificacionInvalidos(NotificacionException):
    """Excepción cuando los datos de la notificación son inválidos"""
    
    def __init__(self, campo: str, valor: str, razon: str):
        self.campo = campo
        self.valor = valor
        self.razon = razon
        super().__init__(f"Datos inválidos en campo '{campo}' con valor '{valor}': {razon}")


class UsuarioInvalido(NotificacionException):
    """Excepción cuando el usuario especificado es inválido"""
    
    def __init__(self, id_usuario: str, razon: str = "Usuario no válido"):
        self.id_usuario = id_usuario
        self.razon = razon
        super().__init__(f"Usuario '{id_usuario}' inválido: {razon}")
