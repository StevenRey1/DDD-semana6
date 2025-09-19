from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from seedworks.aplicacion.comandos import Comando

class PagoData(BaseModel):
    """Datos del pago según especificación"""
    idEvento: str
    idSocio: str
    monto: float
    fechaEvento: datetime

class PagoCommand(BaseModel, Comando):
    """
    Comando unificado para pagos según especificación.
    Maneja tanto Iniciar como Cancelar pagos.
    """
    comando: str  # "Iniciar" | "Cancelar"
    idTransaction: Optional[str] = None
    data: PagoData