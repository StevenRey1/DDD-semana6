import strawberry
import typing
import uuid

from strawberry.types import Info
from bff_web import utils
from bff_web.despachadores import Despachador

from .esquemas import *

@strawberry.type
class Mutation:

    # TODO Agregue objeto de itinerarios o reserva
    @strawberry.mutation
    async def crear_reserva(self, id_usuario: str, id_correlacion: str, info: Info) -> ReservaRespuesta:
        print(f"ID Usuario: {id_usuario}, ID Correlación: {id_correlacion}")
        payload = dict(
            id_usuario = id_usuario,
            id_correlacion = id_correlacion,
            fecha_creacion = utils.time_millis()
        )
        comando = dict(
            id = str(uuid.uuid4()),
            time=utils.time_millis(),
            specversion = "v1",
            type = "ComandoReserva",
            ingestion=utils.time_millis(),
            datacontenttype="AVRO",
            service_name = "BFF Web",
            data = payload
        )
        despachador = Despachador()
        info.context["background_tasks"].add_task(despachador.publicar_mensaje, comando, "comando-crear-reserva", "public/default/comando-crear-reserva")
        
        return ReservaRespuesta(mensaje="Procesando Mensaje", codigo=203)
    
    # TODO Agregue objeto de eventos
    @strawberry.mutation
    async def crear_evento(self, tipoEvento: str, idReferido: str, idSocio: str, monto: float, estadoEvento: str, info: Info) -> EventoRespuesta:
        print(f"Tipo Evento: {tipoEvento}, ID Referido: {idReferido}, ID Socio: {idSocio}, Monto: {monto}, Estado: {estadoEvento}")

        # Crear payload que coincida con el esquema EventoCommand que espera eventoMS
        from datetime import datetime
        comando = dict(
            # Comando enum: Iniciar/Cancelar
            data=dict(
                idTransaction=str(uuid.uuid4()),  # Nuevo ID de transacción
                tipoEvento=tipoEvento,
                idEvento=None,  # Será generado por eventoMS
                idReferido=idReferido,
                idSocio=idSocio,
                monto=float(monto),
                fechaEvento=datetime.utcnow().isoformat() + "Z"
            )
        )

        despachador = Despachador()
        info.context["background_tasks"].add_task(despachador.publicar_mensaje, comando, "comando-saga", "public/default/comando-saga")
        return EventoRespuesta(mensaje="Procesando Mensaje", codigo=203)