import re
from eventosMS.modulos.sagas.aplicacion.comandos.eventos import EventoCommand, EventoCommandPayload, IniciarSagaPago
from eventosMS.modulos.sagas.aplicacion.comandos.referidos import ReferidoCommand
from eventosMS.modulos.sagas.dominio.eventos.eventos import CrearEvento, EventoError, EventoCompensacion, EventoRegistrado
from eventosMS.seedwork.aplicacion.sagas import CoordinadorOrquestacion, Transaccion, Inicio, Fin
from eventosMS.seedwork.aplicacion.comandos import Comando
from eventosMS.seedwork.dominio.eventos import EventoDominio




class CoordinadorPagos(CoordinadorOrquestacion):
    

    def inicializar_pasos(self):
        self.pasos = [
            Inicio(index=0),
            Transaccion(index=1, comando=EventoCommand, evento=CrearEvento, error=EventoError, compensacion=EventoCompensacion, exitosa=True),
            Transaccion(index=2, comando=ReferidoCommand, evento=EventoRegistrado, error=EventoError, compensacion=EventoCompensacion, exitosa=True),
            #Transaccion(index=3, comando=ReferidoCommand, evento=EventoRegistrado, error=EventoError, compensacion=EventoCompensacion, exitosa=True),
            Fin(index=3)
        ]

    def iniciar(self):
        self.persistir_en_saga_log(self.pasos[0])
    
    def terminar(self):
        self.persistir_en_saga_log(self.pasos[-1])

    def persistir_en_saga_log(self, mensaje):
        # TODO Persistir estado en DB
        # Probablemente usted podría usar un repositorio para ello
        ...

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


# TODO Agregue un Listener/Handler para que se puedan redireccionar eventos de dominio
def oir_mensaje(mensaje):
    print("type of message:", type(mensaje))
    if isinstance(mensaje, EventoDominio):
        coordinador = CoordinadorPagos()
        coordinador.inicializar_pasos()
        coordinador.procesar_evento(mensaje)
    else:
        raise NotImplementedError("El mensaje no es evento de Dominio")