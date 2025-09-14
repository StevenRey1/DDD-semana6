from seedwork.aplicacion.comandos import ComandoHandler
from seedwork.infraestructura.uow import UnidadTrabajoPuerto
from seedwork.aplicacion.comandos import ejecutar_commando as comando
from modulos.referidos.aplicacion.comandos.generar_referido import GenerarReferido
from modulos.referidos.dominio.fabricas import FabricaReferidos
from modulos.referidos.infraestructura.fabricas import FabricaRepositorio
from modulos.referidos.infraestructura.repositorios import RepositorioReferidosPostgreSQL
from modulos.referidos.infraestructura.mapeadores import MapeadorReferido
from modulos.referidos.infraestructura.dto import Referido as ReferidoInfra
from modulos.referidos.dominio.eventos import VentaReferidaConfirmada # Import the event
from seedwork.infraestructura.utils import broker_host # Import broker_host
import uuid
import pulsar, _pulsar # Import pulsar client
import json # For serializing event data
from datetime import datetime # For event timestamp

# Initialize Pulsar client and producer globally or as a class attribute
# For simplicity, let's initialize it here. In a real app, consider a proper lifecycle management.
_pulsar_client = None
_pulsar_producer = None

def get_pulsar_client_and_producer():
    global _pulsar_client, _pulsar_producer
    if _pulsar_client is None:
        _pulsar_client = pulsar.Client(f'pulsar://{broker_host()}:6650')
    if _pulsar_producer is None:
        _pulsar_producer = _pulsar_client.create_producer('eventos-referido-confirmado') # Topic name
    return _pulsar_client, _pulsar_producer


class GenerarReferidoHandler(ComandoHandler):
    def __init__(self):
        self._fabrica_repositorio: FabricaRepositorio = FabricaRepositorio()
        self._fabrica_referidos: FabricaReferidos = FabricaReferidos()

    @property
    def fabrica_repositorio(self):
        return self._fabrica_repositorio
    
    @property
    def fabrica_referidos(self):
        return self._fabrica_referidos

    def handle(self, commando: GenerarReferido):
        print("DEBUG: Inside GenerarReferidoHandler.handle")
        print(f"DEBUG: Command received: {commando}")

        referido_infra_id = str(uuid.uuid4())

        referido_dto = ReferidoInfra(
            id=referido_infra_id,
            id_socio=commando.idSocio,
            id_evento=commando.idEvento,
            tipo_evento=commando.tipoEvento,
            id_referido=commando.idReferido,
            monto=commando.monto,
            estado=commando.estado,
            fecha_evento=commando.fechaEvento
        )
        
        print(f"DEBUG: ReferidoInfra object created: {referido_dto}")

        repositorio = self.fabrica_repositorio.crear_objeto(RepositorioReferidosPostgreSQL.__class__)
        
        print("DEBUG: Calling UnidadTrabajoPuerto.registrar_batch")
        UnidadTrabajoPuerto.registrar_batch(repositorio.agregar, referido_dto)
        print("DEBUG: Calling UnidadTrabajoPuerto.commit")
        UnidadTrabajoPuerto.commit()
        print("DEBUG: UnidadTrabajoPuerto.commit finished")

        # Publish VentaReferidaConfirmada event
        try:
            _pulsar_client, _pulsar_producer = get_pulsar_client_and_producer()
            
            evento_confirmado = VentaReferidaConfirmada(
                id_evento=uuid.UUID(commando.idEvento),
                id_socio=uuid.UUID(commando.idSocio),
                monto=commando.monto,
                fecha_evento=datetime.now() # Use current time for event
            )
            
            # Serialize event to JSON
            event_data = {
                "idEvento": str(evento_confirmado.id_evento),
                "idSocio": str(evento_confirmado.id_socio),
                "monto": evento_confirmado.monto,
                "fechaEvento": evento_confirmado.fecha_evento.isoformat()
            }
            
            _pulsar_producer.send(json.dumps(event_data).encode('utf-8'))
            print(f"DEBUG: Published VentaReferidaConfirmada event: {event_data}")
        except Exception as e:
            print(f"ERROR: Failed to publish VentaReferidaConfirmada event: {e}")
            # Handle error, e.g., log it, retry, or use an outbox pattern

@comando.register(GenerarReferido)
def ejecutar_comando_generar_referido(comando: GenerarReferido):
    handler = GenerarReferidoHandler()
    handler.handle(comando)
