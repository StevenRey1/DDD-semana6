
from dataclasses import dataclass
from eventosMS.modulos.sagas.dominio.eventos.eventos import EventoRegistradoPayload
from eventosMS.seedwork.aplicacion.comandos import Comando, ComandoHandler
from eventosMS.seedwork.aplicacion.comandos import ejecutar_commando as comando
from eventosMS.modulos.sagas.infraestructura.despachadores import Despachador


@dataclass
class EventoCommandPayload():
    idEvento: str = None
    tipoEvento : str = None
    idReferido : str = None
    idSocio : str = None
    monto: float = None
    fechaEvento : str = None

@dataclass
class EventoCommand(Comando):
    idTransaction: str = None
    comando: str = None
    idEvento: str = None
    tipoEvento : str = None
    idReferido : str = None
    idSocio : str = None
    monto: float = None
    fechaEvento : str = None


class IniciarSagaPagoPayload():
    idTransaction: str = None
    idEvento: str = None
    tipoEvento : str = None
    idReferido : str = None
    idSocio : str = None
    monto: float = None
    fechaEvento : str = None
    
@dataclass
class IniciarSagaPago(Comando):
    comando: str = None
    data = IniciarSagaPagoPayload()
    

class EventoError():
    ...

class EventoCompensacion():
    ...
    

class EventoCommandHandler(ComandoHandler):
    def handle(self, commando: EventoCommand):
        print("EventoCommandHandler - Procesando comando EventoCommand")
        print("datos del comando:", commando)
        despachador = Despachador()
        despachador.publicar_evento_command(commando.__dict__)
        print ("✅ Comando EventoCommand publicado exitosamente")
        """ UnidadTrabajoPuerto.registrar_batch(repositorio.agregar, referido)
        UnidadTrabajoPuerto.savepoint()
        UnidadTrabajoPuerto.commit() """


@comando.register(EventoCommand)
def ejecutar_evento_command(comando: EventoCommand):
    print("ejecutar_evento_command")
    handler = EventoCommandHandler()
    handler.handle(comando)
    

           
        
