from seedwork.aplicacion.handlers import Handler
from modulos.referidos.infraestructura.despachadores import Despachador
from modulos.referidos.dominio.eventos import VentaReferidaConfirmada, VentaReferidaRechazada

class HandlerReferidosIntegracion(Handler):

    @staticmethod
    def handle_venta_referida_confirmada(evento: VentaReferidaConfirmada):
        print('===================================================================')
        print(f'¡HANDLER: Evento de dominio VentaReferidaConfirmada recibido! ID: {evento.id_evento}')
        print('===================================================================')
        despachador = Despachador()
        despachador.publicar_evento(evento, 'eventos-referido-confirmado')

    @staticmethod
    def handle_venta_referida_rechazada(evento: VentaReferidaRechazada):
        print('===================================================================')
        print(f'¡HANDLER: Evento de dominio VentaReferidaRechazada recibido! ID: {evento.id_evento}')
        print('===================================================================')
        despachador = Despachador()
        despachador.publicar_evento(evento, 'eventos-referido-rechazado')
