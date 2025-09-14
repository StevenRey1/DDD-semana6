from seedwork.aplicacion.comandos import ComandoHandler
from seedwork.infraestructura.uow import UnidadTrabajoPuerto
from seedwork.aplicacion.comandos import ejecutar_commando as comando
from modulos.referidos.aplicacion.comandos.generar_referido import GenerarReferido
from modulos.referidos.dominio.fabricas import FabricaReferidos
from modulos.referidos.infraestructura.fabricas import FabricaRepositorio
from modulos.referidos.infraestructura.repositorios import RepositorioReferidosPostgreSQL
from modulos.referidos.infraestructura.mapeadores import MapeadorReferido
from modulos.referidos.infraestructura.dto import Referido as ReferidoInfra
import uuid

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

@comando.register(GenerarReferido)
def ejecutar_comando_generar_referido(comando: GenerarReferido):
    handler = GenerarReferidoHandler()
    handler.handle(comando)
