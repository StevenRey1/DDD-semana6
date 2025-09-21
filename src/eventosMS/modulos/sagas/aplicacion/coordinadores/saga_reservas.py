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



class CoordinadorPagos(CoordinadorOrquestacion):
    def __init__(self, correlacion_id: str | None = None):
        """Coordinador de la Saga de Pagos.

        Unificación: usamos id_transaction como correlation id (traza) cuando existe.
        - Si el listener no recibe correlacion_id explícito, se intentará usar id_transaction o id del evento.
        - Ya no se genera un UUID separado para correlation; la trazabilidad se apoya en el id de negocio.
        """
        self._correlacion_id = correlacion_id
        from eventosMS.modulos.sagas.infraestructura.repositorio_saga import RepositorioSaga
        self._repo = RepositorioSaga()
        self._saga_instancia = None

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

    def _asegurar_instancia(self):
        if not self._saga_instancia:
            correlacion = self._correlacion_id or "sin-correlacion"
            self._saga_instancia = self._repo.crear_o_recuperar_saga(self.nombre_saga, correlacion, total_pasos=len(self.pasos)-2)  # Excluye Inicio/Fin
        return self._saga_instancia

    def iniciar(self):
        self.persistir_en_saga_log(self.pasos[0])

    def terminar(self):
        self.persistir_en_saga_log(self.pasos[-1])

    def persistir_en_saga_log(self, mensaje):
        instancia = self._asegurar_instancia()
        if isinstance(mensaje, Inicio):
            self._repo.registrar_step(instancia.id, 0, 'Inicio', 'inicio', 'OK', detalle='Saga iniciada')
        elif isinstance(mensaje, Fin):
            self._repo.registrar_step(instancia.id, mensaje.index, 'Fin', 'fin', 'OK', detalle='Saga finalizada')
            self._repo.actualizar_estado_saga(instancia.id, 'COMPLETED', paso_actual=mensaje.index, finalizada=True)
        elif isinstance(mensaje, Transaccion):
            # Registrar intento de publicar comando
            self._repo.registrar_step(instancia.id, mensaje.index, f'Transaccion-{mensaje.index}', 'publicar_comando', 'PENDING', detalle=f'Comando {mensaje.comando.__name__}')
        else:
            # Mensaje desconocido
            self._repo.registrar_step(instancia.id, -1, 'Desconocido', 'debug', 'OK', detalle=str(type(mensaje)))

    def procesar_evento(self, evento: EventoDominio):
        """Extiende la lógica base para registrar eventos de éxito o error."""
        instancia = self._asegurar_instancia()
        try:
            paso, index = self.obtener_paso_dado_un_evento(evento)
        except Exception as e:
            # Evento no asociado: registramos debug y salimos
            self._repo.registrar_step(instancia.id, -1, 'EventoNoMapeado', 'evento_desconocido', 'OK', detalle=str(type(evento)))
            return

        # Determinar si es error o éxito
        es_error = isinstance(evento, paso.error)
        accion = 'evento_error' if es_error else 'evento_ok'
        estado = 'ERROR' if es_error else 'OK'
        self._repo.registrar_step(instancia.id, index, f'Transaccion-{index}', accion, estado, detalle=type(evento).__name__)

        # Actualizar estado saga si es error
        if es_error:
            self._repo.actualizar_estado_saga(instancia.id, 'FAILED', paso_actual=index)
        else:
            self._repo.actualizar_estado_saga(instancia.id, 'RUNNING', paso_actual=index)

        # Reutilizar flujo base (publicación de siguiente comando o terminación)
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
                idTransaction=evento.id,
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
def oir_mensaje(mensaje):
    print("type of message:", type(mensaje))
    if isinstance(mensaje, EventoDominio):
        # Correlation unificado: usar (correlation_id || id_transaction || id)
        correlation = (
            getattr(mensaje, 'correlation_id', None)
            or getattr(mensaje, 'id_transaction', None)
            or getattr(mensaje, 'id', None)
        )
        coordinador = CoordinadorPagos(correlacion_id=str(correlation) if correlation else None)
        coordinador.inicializar_pasos()
        coordinador.iniciar()
        coordinador.procesar_evento(mensaje)
    else:
        raise NotImplementedError("El mensaje no es evento de Dominio")