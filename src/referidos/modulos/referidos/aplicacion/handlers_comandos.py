from modulos.referidos.aplicacion.comandos.referido_command import ReferidoCommand
from modulos.referidos.infraestructura.despachadores import Despachador
from seedwork.aplicacion.comandos import ejecutar_commando
from seedwork.aplicacion.handlers import Handler
from seedwork.dominio.excepciones import ExcepcionDominio
from seedwork.infraestructura.uow import UnidadTrabajoPuerto
from modulos.referidos.dominio.entidades import Referido
from modulos.referidos.dominio.fabricas import FabricaReferidos
from modulos.referidos.dominio.repositorio import RepositorioReferidos
import uuid
from datetime import datetime
from modulos.referidos.aplicacion.dto import ReferidoDTO
from modulos.referidos.aplicacion.mapeadores import MapeadorReferido
from modulos.referidos.dominio.objetos_valor import EstadoReferido, TipoEvento

class HandlerReferidoCommand(Handler):

    @staticmethod
    @ejecutar_commando.register(ReferidoCommand)
    def handle_referido_command(comando: ReferidoCommand):
        print(f"🔄 [HANDLER] Procesando ReferidoCommand: {comando.comando}")

        despachador = Despachador()
        repositorio = UnidadTrabajoPuerto().repositorio_referidos()
        fabrica_referidos = FabricaReferidos()

        if comando.comando == "Iniciar":
            # Crear un nuevo referido
            referido_id = comando.data.idReferido if comando.data.idReferido else str(uuid.uuid4())
            referido_dto = ReferidoDTO(
                id=str(uuid.uuid4()), # Generate a new UUID for the DTO
                idSocio=str(comando.idSocio),
                idReferido=referido_id,
                idEvento=comando.data.idEvento,
                monto=str(comando.data.monto), # Convert to string as DTO expects string
                estado=EstadoReferido.CONFIRMADO.value,
                fechaEvento=comando.data.fechaEvento.isoformat(),
                tipoEvento=comando.data.tipoEvento,
                fecha_creacion=datetime.now().isoformat(),
                fecha_actualizacion=datetime.now().isoformat()
            )
            mapeador_referido = MapeadorReferido()
            referido = fabrica_referidos.crear_objeto(referido_dto, mapeador_referido)

            # Verificar si el referido ya existe
            referido_existente = repositorio.obtener_por_socio_referido_evento(
                uuid.UUID(comando.idSocio),
                uuid.UUID(referido_id),
                uuid.UUID(comando.data.idEvento)
            )

            if referido_existente:
                print(f"⚠️ [HANDLER] Referido {referido_id} ya existe. Publicando evento de rechazo.")
                despachador.publicar_referido_procesado(
                    datos={
                        "idTransaction": str(comando.idTransaction),
                        "idEvento": str(comando.data.idEvento),
                        "idSocio": str(comando.idSocio),
                        "monto": comando.data.monto,
                        "fechaEvento": comando.data.fechaEvento.isoformat()
                    },
                    estado="rechazado"
                )
                # No agregar al repositorio si ya existe
            else:
                repositorio.agregar(referido)
                UnidadTrabajoPuerto.commit()

                # Publicar evento ReferidoProcesado como confirmado
                despachador.publicar_referido_procesado(
                    datos={
                        "idTransaction": str(comando.idTransaction),
                        "idEvento": str(comando.data.idEvento),
                        "idSocio": str(comando.idSocio),
                        "monto": comando.data.monto,
                        "fechaEvento": comando.data.fechaEvento.isoformat()
                    },
                    estado="confirmado"
                )
                print(f"✅ [HANDLER] Referido {referido_id} iniciado y confirmado.")

        elif comando.comando == "Cancelar":
            try:
                idSocio_uuid = uuid.UUID(comando.idSocio)
                idReferido_uuid = uuid.UUID(comando.data.idReferido)
                idEvento_uuid = uuid.UUID(comando.data.idEvento)
            except ValueError:
                raise ExcepcionDominio("IDs de socio, referido o evento no tienen formato UUID válido.")

            print(f"🔄 [HANDLER] Cancelando referido para idSocio: {idSocio_uuid}, idReferido: {idReferido_uuid}, idEvento: {idEvento_uuid}")
            # Buscar el referido por idSocio, idReferido, y idEvento
            referido = repositorio.obtener_por_socio_referido_evento(idSocio_uuid, idReferido_uuid, idEvento_uuid)
            print(f"🔄 [HANDLER] Referido retrieved from repo: {referido}")
            if not referido:
                raise ExcepcionDominio(f"Referido con idSocio {comando.idSocio}, idReferido {comando.data.idReferido}, idEvento {comando.data.idEvento} no encontrado para cancelar.")

            # Actualizar estado a rechazado
            referido.estado = EstadoReferido.RECHAZADO
            repositorio.actualizar(referido)
            UnidadTrabajoPuerto.commit()

            # Publicar evento ReferidoProcesado como rechazado
            despachador.publicar_referido_procesado(
                datos={
                    "idTransaction": str(comando.idTransaction),
                    "idEvento": str(comando.data.idEvento),
                    "idSocio": str(comando.idSocio),
                    "monto": comando.data.monto,
                    "fechaEvento": comando.data.fechaEvento.isoformat()
                },
                estado="rechazado"
            )
            print(f"❌ [HANDLER] Referido {comando.data.idReferido} cancelado y rechazado.")
        else:
            raise ExcepcionDominio(f"Comando '{comando.comando}' no reconocido.")