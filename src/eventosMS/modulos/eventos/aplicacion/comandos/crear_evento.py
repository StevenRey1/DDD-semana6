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

from typing import Optional

@dataclass
class CrearEvento(Comando):
    tipo: str
    id_socio: str
    id_referido: str
    monto: float
    fecha_evento: str
    comando: Optional[str] = None  # "Iniciar" | "Cancelar"
    id_transaction: Optional[str] = None

class CrearEventoHandler(EventoBaseHandler):

    def handle(self, comando: CrearEvento):
        print(f"EVENTO-DTO-TRANS {comando}")
        # Crear DTO solo con los campos básicos para la BD (sin comando, id_transaction)
        evento_dto = EventoDTO(
            tipo=comando.tipo,
            id_socio=comando.id_socio,
            id_referido=comando.id_referido,
            monto=comando.monto,
            fecha_evento=comando.fecha_evento,
            id_transaction=comando.id_transaction,
        )

        # Siempre crear el evento en BD (flujo original)
        evento: Evento = self.fabrica_eventos.crear_objeto(evento_dto, MapeadorEvento())
        evento.id_transaction = comando.id_transaction

        print(f"EVENTO-DTO-TRANS {evento}")
        evento.crear_evento(evento) # Método del agregado que dispara el evento de dominio

        repositorio = self.fabrica_repositorio.crear_objeto(RepositorioEventos.__class__)

        UnidadTrabajoPuerto.registrar_batch(repositorio.agregar, evento)
        UnidadTrabajoPuerto.savepoint()
        UnidadTrabajoPuerto.commit()


@comando.register(CrearEvento)
def ejecutar_comando_crear_evento(comando: CrearEvento):
    handler = CrearEventoHandler()
    handler.handle(comando)