
from seedwork.aplicacion.handlers import Handler
from modulos.referidos.infraestructura.despachadores import Despachador

class HandlerReferidosIntegracion(Handler):

    @staticmethod
    def handle_evento_creado(evento):
        print('===================================================================')
        print(f'¡HANDLER: Evento de dominio Evento recibido! ID: {evento.id}')
        print('===================================================================')
        # =======================================
        despachador = Despachador()
        # Publicamos el evento en el tópico 'eventos-evento'
        despachador.publicar_evento(evento, 'eventos-evento')

    @staticmethod
    def handle_referido_creado(evento):
        print('===================================================================')
        print(f'¡HANDLER: Evento de dominio ReferidoCreado recibido! ID: {evento.idReferido}')
        print('===================================================================')
        # =======================================
        # Temporal: Comentar publicación para evitar timeout de Pulsar
        print(f'[MOCK] Publicaría evento ReferidoCreado en eventos-referido: {evento}')
        # despachador = Despachador()
        # despachador.publicar_evento(evento, 'eventos-referido')

    @staticmethod
    def handle_referido_confirmado(evento):
        despachador = Despachador()
        despachador.publicar_evento(evento, 'eventos-referido')