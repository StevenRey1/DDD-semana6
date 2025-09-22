from dataclasses import dataclass
from eventosMS.seedwork.aplicacion.comandos import Comando, ComandoHandler
from eventosMS.seedwork.aplicacion.comandos import ejecutar_commando
from eventosMS.modulos.sagas.infraestructura.despachadores import Despachador


@dataclass
class ReferidoCommand(Comando):
    idSocio: str = None
    idReferido: str = None
    idEvento: str = None
    monto: float = None
    estado: str = None
    fechaEvento: str = None
    tipoEvento: str = None
    idTransaction: str = None
    comando: str = None

class ReferidoCommandHandler(ComandoHandler):
    def handle(self, commando: ReferidoCommand):
        print("ReferidoCommandHandler - Procesando comando ReferidoCommand")
        print("datos del comando:", commando)
        despachador = Despachador()
        despachador.publicar_referido_command(commando.__dict__)
        """ UnidadTrabajoPuerto.registrar_batch(repositorio.agregar, referido)
        UnidadTrabajoPuerto.savepoint()
        UnidadTrabajoPuerto.commit() """


@ejecutar_commando.register(ReferidoCommand)
def ejecutar_referido_command(comando: ReferidoCommand):
    print("ejecutar_referido_command")
    handler = ReferidoCommandHandler()
    handler.handle(comando)
    
