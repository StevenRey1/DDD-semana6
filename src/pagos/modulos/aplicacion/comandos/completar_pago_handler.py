from seedworks.aplicacion.comandos import ejecutar_commando
from .base import PagoBaseHandler
from .completar_pago import CompletarPagoCommand
from ...infraestructura.repositorio_postgresql import RepositorioPagosPG
from config.pulsar_config import Settings
import json
from datetime import datetime
from uuid import uuid4

class CompletarPagoHandler(PagoBaseHandler):
    """
    Handler para completar pagos cuando se confirman ventas referidas.
    Lógica de negocio limpia y aislada.
    """
    
    def handle(self, comando: CompletarPagoCommand):
        print(f"🔄 Ejecutando CompletarPagoHandler para evento: {comando.idEvento}")
        
        settings = Settings()
        repo = RepositorioPagosPG(settings.DB_URL)
        
        with repo.SessionLocal() as session:
            # Buscar pago existente
            pago_existente = session.query(repo.PagoORM).filter_by(
                idEvento=comando.idEvento, 
                estado="solicitado"
            ).first()
            
            if pago_existente:
                # Completar pago existente
                pago_existente.estado = "completado"
                session.commit()
                pago_final = pago_existente
                print(f"✅ Pago existente {pago_existente.idPago} completado")
                
            else:
                # Crear nuevo pago completado
                idPago = str(uuid4())
                pago_final = repo.PagoORM(
                    idPago=idPago,
                    idEvento=comando.idEvento,
                    idSocio=comando.idSocio,
                    monto=comando.monto,
                    estado="completado",
                    fechaPago=comando.fechaEvento
                )
                session.add(pago_final)
                session.commit()
                print(f"✅ Nuevo pago {idPago} creado y completado")
            
            # Publicar evento vía outbox
            self._publicar_evento_procesado(repo, pago_final)
            return pago_final
    
    def _publicar_evento_procesado(self, repo, pago):
        """Publica evento PagoProcesado según nueva especificación"""
        evento_pago_procesado = {
            "idTransaction": None,  # No tenemos idTransaction en completar pago
            "idPago": pago.idPago,
            "idEvento": pago.idEvento,
            "idSocio": pago.idSocio,
            "monto": float(pago.monto),
            "estado_pago": "completado",  # Campo renombrado según especificación
            "fechaPago": pago.fechaPago.isoformat()
        }
        
        # Outbox pattern para eventos-pago (tópico actualizado)
        repo.outbox_add("eventos-pago", pago.idPago, json.dumps(evento_pago_procesado))

# Registrar handler usando singledispatch
@ejecutar_commando.register(CompletarPagoCommand)
def ejecutar_comando_completar_pago(comando: CompletarPagoCommand):
    handler = CompletarPagoHandler()
    return handler.handle(comando)