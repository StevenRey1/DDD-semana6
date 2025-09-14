#	•	`GenerarReferidoCommand`: Request de creación de un referido usando parámetros (usuario, embajador, tipo de acción, etc.).
#	•	`ConfirmarVentaReferidaCommand`: Comando para registrar que una venta atribuida a un referido fue confirmada.

# Propósito: Comando para crear un nuevo referido, encapsulando los datos necesarios.

from modulos.referidos.aplicacion.comandos.base import CrearReferidoBaseHandler
from modulos.referidos.infraestructura.mapeadores import MapeadorReferido
from modulos.referidos.aplicacion.dto import ReferidoDTO
from modulos.referidos.dominio.entidades import Referido
from seedwork.infraestructura.uow import UnidadTrabajoPuerto
from seedwork.aplicacion.comandos import Comando
from dataclasses import dataclass, field
from seedwork.aplicacion.comandos import ejecutar_commando as comando
from modulos.referidos.infraestructura.repositorios import RepositorioReferidos

@dataclass
class CrearReferido(Comando):
    idSocio: str
    idReferido: str
    monto: float
    estado: str
    fechaEvento: str
    idEvento: str
    tipoEvento: str
    fecha_creacion: str = field(default_factory=str)
    fecha_actualizacion: str = field(default_factory=str)

class CrearReferidoHandler(CrearReferidoBaseHandler):
    def handle(self, commando: CrearReferido):
        referido_dto = ReferidoDTO(
            idSocio=commando.idSocio,
            idReferido=commando.idReferido,
            monto=commando.monto,
            estado=commando.estado,
            fechaEvento=commando.fechaEvento,
            tipoEvento=commando.tipoEvento,
            idEvento=commando.idEvento,
            fecha_creacion=commando.fecha_creacion,
            fecha_actualizacion=commando.fecha_actualizacion
        )
        referido: Referido = self.fabrica_referidos.crear_objeto(referido_dto, MapeadorReferido())
        print("======================")
        print("CrearReferidoHandler.referido "+str(referido))
        print("======================")
        referido.crear_referido(referido)

        repositorio = self.fabrica_repositorio.crear_objeto(RepositorioReferidos.__class__)

        print("======================")
        print("Referido creado, listo para persistir en BD")
        print("======================")

        UnidadTrabajoPuerto.registrar_batch(repositorio.agregar, referido)
        UnidadTrabajoPuerto.savepoint()
        UnidadTrabajoPuerto.commit()


@comando.register(CrearReferido)
def ejecutar_comando_crear_referido(comando: CrearReferido):
    print("ejecutar_comando_crear_referido")
    handler = CrearReferidoHandler()
    handler.handle(comando)