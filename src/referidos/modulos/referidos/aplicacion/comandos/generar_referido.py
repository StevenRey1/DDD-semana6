from seedwork.aplicacion.comandos import Comando
from dataclasses import dataclass

@dataclass
class GenerarReferido(Comando):
    idSocio: str
    idEvento: str
    tipoEvento: str
    idReferido: str
    monto: float
    estado: str
    fechaEvento: str
