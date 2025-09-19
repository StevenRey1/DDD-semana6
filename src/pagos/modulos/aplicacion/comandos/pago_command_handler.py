from seedworks.aplicacion.comandos import ejecutar_commando
from .base import PagoBaseHandler
from .pago_command import PagoCommand
from ...infraestructura.repositorio_postgresql import RepositorioPagosPG
from config.pulsar_config import Settings
import json
from datetime import datetime
from uuid import uuid4

class PagoCommandHandler(PagoBaseHandler):
    """
    Handler unificado para PagoCommand.
    Maneja tanto comando 'Iniciar' como 'Cancelar' según especificación.
    """
    
    def handle(self, comando: PagoCommand):
        print(f"🔄 Ejecutando PagoCommandHandler - Comando: {comando.comando}")
        
        if comando.comando == "Iniciar":
            return self._iniciar_pago(comando)
        elif comando.comando == "Cancelar":
            return self._cancelar_pago(comando)
        else:
            raise ValueError(f"Comando no soportado: {comando.comando}")
    
    def _iniciar_pago(self, comando: PagoCommand):
        """Lógica para iniciar un pago"""
        settings = Settings()
        repo = RepositorioPagosPG(settings.DB_URL)
        
        with repo.SessionLocal() as session:
            # Verificar si ya existe
            pago_existente = session.query(repo.PagoORM).filter_by(
                idEvento=comando.data.idEvento
            ).first()
            
            if pago_existente:
                print(f"⚠️ Pago ya existe para evento {comando.data.idEvento}")
                return pago_existente
            
            # Crear nuevo pago
            idPago = str(uuid4())
            pago_orm = repo.PagoORM(
                idPago=idPago,
                idEvento=comando.data.idEvento,
                idSocio=comando.data.idSocio,
                monto=comando.data.monto,
                estado="solicitado",
                fechaPago=comando.data.fechaEvento
            )
            session.add(pago_orm)
            session.commit()
            
            # Publicar evento PagoProcesado
            self._publicar_evento_procesado(repo, pago_orm, comando.idTransaction, "solicitado")
            print(f"✅ Pago {idPago} iniciado exitosamente")
            
            return pago_orm
    
    def _cancelar_pago(self, comando: PagoCommand):
        """Lógica para cancelar un pago"""
        settings = Settings()
        repo = RepositorioPagosPG(settings.DB_URL)
        
        with repo.SessionLocal() as session:
            # Buscar pago existente
            pago_existente = session.query(repo.PagoORM).filter_by(
                idEvento=comando.data.idEvento
            ).first()
            
            if not pago_existente:
                raise ValueError(f"Pago no encontrado para evento {comando.data.idEvento}")
            
            # Cancelar pago
            pago_existente.estado = "rechazado"
            session.commit()
            
            # Publicar evento PagoProcesado
            self._publicar_evento_procesado(repo, pago_existente, comando.idTransaction, "rechazado")
            print(f"✅ Pago {pago_existente.idPago} cancelado exitosamente")
            
            return pago_existente
    
    def _publicar_evento_procesado(self, repo, pago, idTransaction, estado):
        """Publica evento PagoProcesado según especificación"""
        evento_pago_procesado = {
            "idTransaction": idTransaction,
            "idPago": pago.idPago,
            "idEvento": pago.idEvento,
            "idSocio": pago.idSocio,
            "monto": float(pago.monto),
            "estado_pago": estado,
            "fechaPago": pago.fechaPago.isoformat()
        }
        
        # Outbox pattern para eventos-pago
        repo.outbox_add("eventos-pago", pago.idPago, json.dumps(evento_pago_procesado))

# Registrar handler usando singledispatch
@ejecutar_commando.register(PagoCommand)
def ejecutar_pago_command(comando: PagoCommand):
    handler = PagoCommandHandler()
    return handler.handle(comando)