from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from ..modulos.aplicacion.dto import PagoIntegracion
from ..modulos.aplicacion.comandos.solicitar_pago import SolicitarPagoCommand
from ..modulos.aplicacion.queries.obtener_estado_pago import ObtenerEstadoPagoQuery
from ..modulos.infraestructura.repositorio_postgresql import RepositorioPagosPG
from ..config.pulsar_config import settings

router = APIRouter()

# Dependency para obtener sesión DB
from fastapi import Request

def get_db(request: Request):
    repo: RepositorioPagosPG = request.app.state.repo
    return repo.SessionLocal()

@router.post("/pagos", status_code=status.HTTP_202_ACCEPTED)
def solicitar_pago(cmd: SolicitarPagoCommand, db: Session = Depends(get_db)):
    repo = RepositorioPagosPG(settings.DB_URL)
    pago = repo.by_id(cmd.idEvento)
    if pago:
        return {"operation_id": pago.idPago, "status_url": f"/pagos/{pago.idPago}"}
    pago = repo.guardar(Pago.solicitar(cmd.idEvento, cmd.idSocio, cmd.monto))
    # Envelope y outbox
    envelope = {
        "meta": {"event_id": pago.idPago, "schema_version": "v1", "occurred_at": int(pago.fechaPago.timestamp()*1000), "producer": settings.SERVICE_NAME, "correlation_id": cmd.idEvento, "causation_id": pago.idPago},
        "key": pago.idPago,
        "state": PagoIntegracion(**pago.__dict__).dict()
    }
    repo.outbox_add(settings.TOPIC_PAGOS, pago.idPago, json.dumps(envelope))
    return {"operation_id": pago.idPago, "status_url": f"/pagos/{pago.idPago}"}

@router.get("/pagos/{idPago}", response_model=PagoIntegracion)
def obtener_estado_pago(idPago: str, db: Session = Depends(get_db)):
    repo = RepositorioPagosPG(settings.DB_URL)
    pago = repo.by_id(idPago)
    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    return PagoIntegracion(**pago.__dict__)
