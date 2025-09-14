# Propósito: Define el comando ActualizarEventoPago y su handler, que orquesta la 
# actualización de un evento cuando se completa un pago.

from datetime import datetime
from modulos.eventos.aplicacion.dto import ActualizarEventoPagoDTO
from modulos.eventos.dominio.entidades import Evento
from modulos.eventos.dominio.repositorios import RepositorioEventos
from modulos.eventos.infraestructura.mapeadores import MapeadorEvento
from seedwork.aplicacion.comandos import Comando
from .base import EventoBaseHandler
from dataclasses import dataclass
from seedwork.aplicacion.comandos import ejecutar_commando as comando
from seedwork.infraestructura.uow import UnidadTrabajoPuerto


@dataclass
class ActualizarEventoPago(Comando):
    """
    Comando para actualizar un evento con información de pago completado.
    
    Attributes:
        id_evento: Identificador único del evento a actualizar
        id_pago: Identificador del pago asociado
        estado_pago: Estado del pago (completado, fallido, etc.)
        ganancia: Ganancia calculada del evento
        fecha_pago: Fecha cuando se completó el pago
        monto_pago: Monto del pago realizado
    """
    id_evento: str
    id_pago: str
    estado_pago: str
    ganancia: float
    fecha_pago: str
    monto_pago: float


class ActualizarEventoPagoHandler(EventoBaseHandler):
    """
    Handler que procesa el comando ActualizarEventoPago siguiendo arquitectura hexagonal.
    
    Se encarga de:
    1. Buscar el evento existente en el repositorio
    2. Actualizar los datos del evento con información del pago
    3. Disparar eventos de dominio correspondientes
    4. Persistir los cambios usando la unidad de trabajo
    """

    def handle(self, comando: ActualizarEventoPago):
        """
        Procesa la actualización del evento con información de pago.
        
        Args:
            comando: Comando con los datos para actualizar el evento
            
        Raises:
            EventoNoEncontrado: Si el evento no existe
            ErrorActualizacion: Si hay problemas en la actualización
        """
        
        
        # Obtener repositorio del dominio
        repositorio = self.fabrica_repositorio.crear_objeto(RepositorioEventos.__class__)
        
        # Buscar el evento existente
        evento_existente = repositorio.obtener_por_id(comando.id_evento)
        print(f"🔍 Evento encontrado: {evento_existente} para actualización")
        
        if not evento_existente:
            from modulos.eventos.dominio.excepciones import EventoNoEncontrado
            raise EventoNoEncontrado(f"Evento con ID {comando.id_evento} no encontrado")
        
        # Actualizar el evento con información del pago usando el método de dominio
        evento_existente.actualizar_con_pago(
            id_pago=comando.id_pago,
            estado_pago=comando.estado_pago,
            ganancia=comando.ganancia,
            fecha_pago=comando.fecha_pago,
            monto_pago=comando.monto_pago
        )
        print(f"✅ Evento {evento_existente.id} actualizado con pago {comando.id_pago}")

        # Usar la unidad de trabajo para persistir los cambios
        UnidadTrabajoPuerto.registrar_batch(repositorio.actualizar, evento_existente)
        UnidadTrabajoPuerto.savepoint()
        UnidadTrabajoPuerto.commit()


@comando.register(ActualizarEventoPago)
def ejecutar_comando_actualizar_evento_pago(comando: ActualizarEventoPago):
    """
    Función registrada para ejecutar el comando ActualizarEventoPago.
    
    Args:
        comando: Comando a ejecutar
    """
    handler = ActualizarEventoPagoHandler()
    handler.handle(comando)