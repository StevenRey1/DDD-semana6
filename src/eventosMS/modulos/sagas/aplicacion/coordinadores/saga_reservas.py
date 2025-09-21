import re
from eventosMS.modulos.sagas.aplicacion.comandos.eventos import EventoCommand, EventoCommandPayload, IniciarSagaPago
from eventosMS.modulos.sagas.aplicacion.comandos.referidos import ReferidoCommand
from eventosMS.modulos.sagas.dominio.eventos.eventos import CrearEvento, EventoError, EventoCompensacion, EventoRegistrado
from eventosMS.seedwork.aplicacion.sagas import CoordinadorOrquestacion, Transaccion, Inicio, Fin
from eventosMS.seedwork.aplicacion.comandos import Comando
from eventosMS.seedwork.dominio.eventos import EventoDominio
from eventosMS.modulos.sagas.aplicacion.comandos.pagos import PagoCommand
from eventosMS.modulos.sagas.dominio.eventos.referidos import ReferidoProcesado
from eventosMS.modulos.sagas.dominio.eventos.pagos import PagoProcesado
from eventosMS.modulos.sagas.infraestructura.repositorio_saga import RepositorioSaga


class CoordinadorPagos(CoordinadorOrquestacion):
    def __init__(self, correlacion_id: str | None = None, app=None):
        self._correlacion_id = correlacion_id
        self._repo = RepositorioSaga(app) if app else None

    @property
    def nombre_saga(self):
        return "SagaPagos"

    def inicializar_pasos(self):
        self.pasos = [
            Inicio(index=0),
            Transaccion(index=1, comando=EventoCommand, evento=CrearEvento, error=EventoError, compensacion=EventoCompensacion, exitosa=True),
            Transaccion(index=2, comando=ReferidoCommand, evento=EventoRegistrado, error=EventoError, compensacion=EventoCompensacion, exitosa=True),
            Transaccion(index=3, comando=PagoCommand, evento=ReferidoProcesado, error=EventoError, compensacion=EventoCompensacion, exitosa=True),
            Transaccion(index=4, comando=None, evento=PagoProcesado, error=EventoError, compensacion=EventoCompensacion, exitosa=True),
            Fin(index=5)
        ]

    def persistir_en_saga_log(self, mensaje):  # type: ignore[override]
        """Compatibilidad con la interfaz abstracta original.

        El flujo normal YA registra usando helpers. Aquí sólo aseguramos que si
        algún código legado llama a este método, no falle y (en caso de Inicio/Fin)
        se garantice la existencia del registro.
        """
        if not self._correlacion_id:
            return
        from eventosMS.seedwork.aplicacion.sagas import Inicio as _Inicio, Fin as _Fin
        if isinstance(mensaje, _Inicio):
            # Evitar duplicar si ya existe un inicio para esa transacción
            if not self._repo.ultimo(self._correlacion_id):
                self._repo.registrar_inicio(self._correlacion_id)
        elif isinstance(mensaje, _Fin):
            self._repo.registrar_fin(self._correlacion_id, paso=getattr(mensaje, 'index', -1), exito=True)


    def iniciar(self):
        print("Iniciando  de pagos..." + str(self._correlacion_id))
        if self._correlacion_id:
            self._repo.registrar_inicio(self._correlacion_id)

    def terminar(self):
        # Paso final = índice del objeto Fin (último en la lista)
        if self._correlacion_id:
            paso_fin = self.pasos[-1].index if isinstance(self.pasos[-1], Fin) else len(self.pasos)-1
            self._repo.registrar_fin(self._correlacion_id, paso=paso_fin, exito=True)

    # ------------------ Sobre-escrituras para logging simplificado ------------------ #
    def publicar_comando(self, evento: EventoDominio, tipo_comando: type):  # type: ignore[override]
        """Publicar comando registrándolo primero en el saga_log.

        Buscamos el índice de la transacción cuyo comando (o compensación) coincide con el tipo_comando.
        Guardamos el nombre del comando (clase) y marcamos PENDING.
        """
        if not self._correlacion_id:
            return
        # Encontrar índice del paso asociado al comando o compensación
        paso_index = None
        for p in self.pasos:
            if isinstance(p, Transaccion) and (p.comando == tipo_comando or p.compensacion == tipo_comando):
                paso_index = p.index
                break
        if paso_index is None:
            paso_index = -1
        # Construir comando real
        comando = self.construir_comando(evento, tipo_comando)
        if comando is None:
            return
        self._repo.registrar_comando(self._correlacion_id, type(comando).__name__, paso_index, pendiente=True)
        # Ejecutar comando (delegamos en infraestructura existente)
        from eventosMS.seedwork.aplicacion.comandos import ejecutar_commando
        ejecutar_commando(comando)

    def procesar_evento(self, evento: EventoDominio):
        """Registrar el evento (ok o error) y delegar lógica de orquestación en la superclase."""
        if not self._correlacion_id:
            return
        try:
            paso, index = self.obtener_paso_dado_un_evento(evento)
        except Exception:
            # Evento no reconocido: lo ignoramos en este modelo simplificado
            return
        
        print(f"Procesando evento test {type(evento).__name__} en paso {index}")
        if paso.index == 1:
            self.iniciar()

        if isinstance(paso, Transaccion):
            if isinstance(evento, paso.error):
                self._repo.registrar_evento_error(self._correlacion_id, type(evento).__name__, paso.index)
            elif isinstance(evento, paso.evento):
                self._repo.registrar_evento_ok(self._correlacion_id, type(evento).__name__, paso.index)

        # Delegar a la lógica de orquestación (publicará comando o terminará)
        super().procesar_evento(evento)

    def construir_comando(self, evento: EventoDominio, tipo_comando: type):
        # TODO Transforma un evento en la entrada de un comando
        # Por ejemplo si el evento que llega es ReservaCreada y el tipo_comando es PagarReserva
        # Debemos usar los atributos de ReservaCreada para crear el comando PagarReserva
        print("construir_comando - Construyendo comando")
        print("evento:", evento)
        print("tipo_comando:", tipo_comando)

        if isinstance(evento, CrearEvento) and tipo_comando == EventoCommand:
            print("construir_comando - Construyendo comando para evento CrearEvento")
            
            comando = EventoCommand(
                idTransaction=evento.id_transaction,
                comando=evento.comando,
                tipoEvento=evento.tipo,
                idReferido=evento.id_referido,
                idSocio=evento.id_socio,
                monto=evento.monto,
                fechaEvento=evento.fecha_evento
                
            )
            print("construir_comando - Comando construido:", comando)
            return comando
        elif isinstance(evento, EventoRegistrado) and tipo_comando == ReferidoCommand:
            print("construir_comando - Construyendo comando para evento EventoRegistrado")
            comando = ReferidoCommand(
                idSocio=evento.idSocio,
                idReferido=evento.idReferido,
                idEvento=evento.idEvento,
                monto=evento.monto,
                estado=evento.estado,
                fechaEvento=evento.fechaEvento,
                tipoEvento=evento.tipoEvento,
                idTransaction=evento.idTransaction,
                comando=evento.comando
            )
            return comando
        elif isinstance(evento, ReferidoProcesado) and tipo_comando == PagoCommand:
            print("construir_comando - Construyendo comando para evento ReferidoProcesado")
            comando = PagoCommand(
                idTransaction=evento.idTransaction,
                comando="Iniciar",
                idEvento=evento.idEvento,
                idSocio=evento.idSocio,
                monto=evento.monto,
                fechaEvento=evento.fechaEvento
            )
            return comando


# TODO Agregue un Listener/Handler para que se puedan redireccionar eventos de dominio
def oir_mensaje(mensaje, app):
    if isinstance(mensaje, EventoDominio):
        correlation = (
            getattr(mensaje, 'idTransaction', None)
        )
        coordinador = CoordinadorPagos(correlacion_id=str(correlation) if correlation else None, app=app)

        coordinador.inicializar_pasos()
        coordinador.procesar_evento(mensaje)