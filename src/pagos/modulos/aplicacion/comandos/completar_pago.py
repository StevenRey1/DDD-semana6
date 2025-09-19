from pydantic import BaseModel
from datetime import datetime
from seedworks.aplicacion.comandos import Comando

class CompletarPagoCommand(BaseModel, Comando):
    idEvento: str
    idSocio: str
    monto: float
    fechaEvento: datetime