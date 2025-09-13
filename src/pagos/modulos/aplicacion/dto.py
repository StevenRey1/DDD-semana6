from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class PagoIntegracion(BaseModel):
    idPago: str
    idEvento: str
    idSocio: str
    monto: float
    estado: str
    fechaPago: datetime
