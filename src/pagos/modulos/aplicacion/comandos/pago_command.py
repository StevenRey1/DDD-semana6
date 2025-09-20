from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
from seedworks.aplicacion.comandos import Comando
from enum import Enum

class TipoComandoPago(str, Enum):
    INICIAR = "Iniciar"
    CANCELAR = "Cancelar"
    COMPLETAR = "Completar"

class PagoData(BaseModel):
    """Datos del pago según especificación"""
    idEvento: str
    idSocio: str
    monto: float
    fechaEvento: datetime

class PagoCommand(BaseModel, Comando):
    """
    Comando unificado para pagos según especificación.
    Maneja Iniciar, Cancelar y Completar pagos.
    """
    comando: TipoComandoPago  # Enum restringido
    idTransaction: Optional[str] = None
    data: PagoData

    @field_validator('data')
    def validar_monto(cls, v):
        if v.monto <= 0:
            raise ValueError("monto debe ser > 0")
        return v