from pydantic import BaseModel
from typing import Optional
from seedworks.aplicacion.queries import Query

class ObtenerEstadoPagoQuery(BaseModel, Query):
    idPago: str
    idTransaction: Optional[str] = None  # Según especificación
