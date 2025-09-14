# Propósito: Define el comando CrearPago y su handler, que orquesta la 
# creación de un nuevo pago.

from datetime import datetime
from modulos.eventos.aplicacion.dto import EventoDTO
from modulos.eventos.dominio.entidades import Evento
from modulos.eventos.dominio.repositorios import RepositorioEventos
from modulos.eventos.infraestructura.mapeadores import MapeadorEvento
from seedwork.aplicacion.comandos import Comando
from .base import EventoBaseHandler
from dataclasses import dataclass, field
from seedwork.aplicacion.comandos import ejecutar_commando as comando

from seedwork.infraestructura.uow import UnidadTrabajoPuerto

@dataclass
class CrearEvento(Comando):
    tipo: str
    id_socio: str
    id_referido: str
    monto: float
    fecha_evento: str

class CrearEventoHandler(EventoBaseHandler):

    def handle(self, comando: CrearEvento):
        
        evento_dto = EventoDTO(
            tipo=comando.tipo,
            id_socio=comando.id_socio,
            id_referido=comando.id_referido,
            monto=comando.monto,
            fecha_evento=comando.fecha_evento
        )

        evento: Evento = self.fabrica_eventos.crear_objeto(evento_dto, MapeadorEvento())
        evento.crear_evento(evento) # Método del agregado que dispara el evento de dominio

        repositorio = self.fabrica_repositorio.crear_objeto(RepositorioEventos.__class__)

        UnidadTrabajoPuerto.registrar_batch(repositorio.agregar, evento)
        UnidadTrabajoPuerto.savepoint()
        UnidadTrabajoPuerto.commit()


@comando.register(CrearEvento)
def ejecutar_comando_crear_evento(comando: CrearEvento):
    handler = CrearEventoHandler()
    handler.handle(comando)