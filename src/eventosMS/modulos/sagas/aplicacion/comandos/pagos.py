
from dataclasses import dataclass
from eventosMS.seedwork.aplicacion.comandos import Comando, ComandoHandler
from eventosMS.seedwork.aplicacion.comandos import ejecutar_commando
from eventosMS.modulos.sagas.infraestructura.despachadores import Despachador

class PagarReserva():
    ...

class RevertirPago():
    ...

@dataclass
class PagoCommand(Comando):
    comando: str = None  # "Iniciar" | "Cancelar"
    idTransaction: str = None  # Opcional
    idEvento: str = None
    idSocio: str = None
    monto: float = None
    fechaEvento: str = None  


class PagoCommandHandler(ComandoHandler):
    def handle(self, commando: PagoCommand):
        print("PagoCommandHandler - Procesando comando PagoCommand")
        print("datos del comando:", commando)
        despachador = Despachador()
        despachador.publicar_pago_command(commando.__dict__)
        """ UnidadTrabajoPuerto.registrar_batch(repositorio.agregar, referido)
        UnidadTrabajoPuerto.savepoint()
        UnidadTrabajoPuerto.commit() """


@ejecutar_commando.register(PagoCommand)
def ejecutar_pago_command(comando: PagoCommand):
    print("ejecutar_pago_command")
    handler = PagoCommandHandler()
    handler.handle(comando)