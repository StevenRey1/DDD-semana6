from seedworks.aplicacion.comandos import ejecutar_commando
from .base import PagoBaseHandler
from .solicitar_pago import SolicitarPagoCommand
from ...infraestructura.repositorio_postgresql import RepositorioPagosPG
from config.pulsar_config import Settings
import json
from datetime import datetime
from uuid import uuid4

class SolicitarPagoHandler(PagoBaseHandler):
    """
    Handler que implementa la lógica de negocio para solicitar pagos.
    Sigue el patrón CQRS delegando la persistencia al repositorio.
    """
    
    def handle(self, comando: SolicitarPagoCommand):
        print(f"🔄 Ejecutando SolicitarPagoHandler para evento: {comando.idEvento}")
        
        # Crear instancia del repositorio
        settings = Settings()
        repo = RepositorioPagosPG(settings.DB_URL)
        
        # Verificar si ya existe un pago para este evento
        with repo.SessionLocal() as session:
            pago_existente = session.query(repo.PagoORM).filter_by(idEvento=comando.idEvento).first()
            
            if pago_existente:
                print(f"⚠️ Pago ya existe para evento {comando.idEvento}")
                return pago_existente
            
            # Crear nuevo pago
            idPago = str(uuid4())
            pago_orm = repo.PagoORM(
                idPago=idPago,
                idEvento=comando.idEvento,
                idSocio=comando.idSocio,
                monto=comando.monto,
                estado="solicitado",
                fechaPago=comando.fechaEvento
            )
            session.add(pago_orm)
            session.commit()
            
            # Preparar evento PagoSolicitado para outbox
            envelope = {
                "meta": {
                    "event_id": idPago,
                    "schema_version": "v1", 
                    "occurred_at": int(datetime.utcnow().timestamp()*1000),
                    "producer": "pagos-service",
                    "correlation_id": comando.idEvento,
                    "causation_id": idPago
                },
                "key": idPago,
                "state": {
                    "idPago": idPago,
                    "idEvento": comando.idEvento,
                    "idSocio": comando.idSocio,
                    "monto": float(comando.monto),
                    "estado": "solicitado",
                    "fechaPago": comando.fechaEvento.isoformat()
                }
            }
            
            # Agregar evento al outbox para publicación confiable
            repo.outbox_add("eventos-pago", idPago, json.dumps(envelope))
            print(f"✅ Pago {idPago} solicitado exitosamente")
            
            return pago_orm

# Registrar handler usando singledispatch igual que EventosMS
@ejecutar_commando.register(SolicitarPagoCommand)
def ejecutar_comando_solicitar_pago(comando: SolicitarPagoCommand):
    handler = SolicitarPagoHandler()
    return handler.handle(comando)