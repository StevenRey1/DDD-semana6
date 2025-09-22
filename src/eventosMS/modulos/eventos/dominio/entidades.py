"""
Entidades del dominio de Eventos
"""
from __future__ import annotations
from dataclasses import dataclass, field
from seedwork.dominio.entidades import AgregacionRaiz
from .objetos_valor import TipoEvento
from .eventos import EventoRegistrado
from datetime import datetime
from uuid import UUID
from typing import Optional


@dataclass
class Evento(AgregacionRaiz):
    """
    Entidad principal que representa un evento en el sistema
    """
    id: UUID = field(default=None)
    tipo: TipoEvento = field(default=None)
    id_socio: UUID = field(default=None)
    id_referido: Optional[UUID] = field(default=None)
    monto: float = field(default=0.0)
    ganancia: float = field(default=0.0)
    estado: str = field(default="pendiente")
    fecha_evento: datetime = field(default=None)
    comando: Optional[str] = field(default=None)  # "Iniciar" | "Cancelar"
    id_transaction: Optional[str] = field(default=None)

    def crear_evento(self, evento: Evento):
        """
        Método para iniciar la creación del agregado.
        Dispara el evento de dominio inicial.
        """
        self.tipo = evento.tipo
        self.id_socio = evento.id_socio
        self.id_referido = evento.id_referido
        self.monto = evento.monto
        self.ganancia = evento.ganancia
        self.estado = evento.estado
        self.fecha_creacion = evento.fecha_creacion
        self.fecha_actualizacion = evento.fecha_actualizacion
        self.fecha_evento = evento.fecha_evento
        self.comando = evento.comando
        self.id_transaction = evento.id_transaction

        self.agregar_evento(EventoRegistrado(
            evento_id=self.id,
            tipo_evento=self.tipo.valor,
            id_referido=self.id_referido,
            id_socio=self.id_socio,
            monto=self.monto,
            ganancia=self.ganancia,
            estado=self.estado,
            fecha_evento=self.fecha_evento,
            comando=self.comando,
            id_transaction=self.id_transaction
        ))

    def actualizar_con_pago(self, id_pago: str, estado_pago: str, ganancia: float, 
                           fecha_pago: str, monto_pago: float):
        """
        Actualiza el evento con información de pago completado.
        Dispara evento de dominio correspondiente.
        
        Args:
            id_pago: Identificador del pago asociado
            estado_pago: Estado del pago (completado, fallido, etc.)
            ganancia: Ganancia calculada del evento
            fecha_pago: Fecha cuando se completó el pago
            monto_pago: Monto del pago realizado
        """
        # Actualizar estado del evento basado en el estado del pago
        if estado_pago == "completado":
            self.estado = "pago_completado"
        elif estado_pago == "fallido":
            self.estado = "pago_fallido"
        else:
            self.estado = f"pago_{estado_pago}"
        
        # Actualizar ganancia con el valor calculado
        self.ganancia = ganancia
        
        # Actualizar timestamp de modificación
        self.fecha_actualizacion = datetime.now()
        
        # Disparar evento de dominio para notificar la actualización
        from .eventos import EventoPagoActualizado
        self.agregar_evento(EventoPagoActualizado(
            evento_id=self.id,
            id_pago=id_pago,
            estado_anterior=self.estado,
            estado_nuevo=self.estado,
            ganancia_anterior=self.ganancia,
            ganancia_nueva=ganancia,
            fecha_pago=fecha_pago,
            monto_pago=monto_pago
        ))
