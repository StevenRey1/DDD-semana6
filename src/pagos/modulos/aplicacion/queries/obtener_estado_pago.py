from pydantic import BaseModel

class ObtenerEstadoPagoQuery(BaseModel):
    idPago: str
