from pydantic import BaseModel
from datetime import datetime

class SolicitarPagoCommand(BaseModel):
    idEvento: str
    idSocio: str
    monto: float
    fechaEvento: datetime
