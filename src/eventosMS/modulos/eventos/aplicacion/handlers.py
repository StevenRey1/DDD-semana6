"""
Handlers de aplicación para el módulo de Eventos
"""
from modulos.eventos.infraestructura.despachadores import Despachador
from seedwork.aplicacion.handlers import Handler

class HandlerEventoIntegracion(Handler):

    @staticmethod
    def handle_evento_registrado(evento):
        print('===================================================================')
        print(f'¡HANDLER: Evento de dominio EventoRegistrado recibido! ID: {evento.evento_id}')
        print('===================================================================')
        # =======================================
        despachador = Despachador()
        # Publicamos el evento en el tópico 'eventos'
        despachador.publicar_evento(evento, 'eventos-tracking')