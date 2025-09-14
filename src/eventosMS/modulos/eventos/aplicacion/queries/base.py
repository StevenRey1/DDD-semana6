# Propósito: Clase base para los handlers de comandos de eventos, para 
# inyectar dependencias comunes.

from seedwork.aplicacion.comandos import ComandoHandler
from modulos.eventos.infraestructura.fabricas import FabricaRepositorio
from modulos.eventos.dominio.fabricas import FabricaEventos

class EventoQueryBaseHandler(ComandoHandler):
    def __init__(self):
        self._fabrica_repositorio: FabricaRepositorio = FabricaRepositorio()
        self._fabrica_eventos: FabricaEventos = FabricaEventos()

    @property
    def fabrica_repositorio(self):
        return self._fabrica_repositorio
    
    @property
    def fabrica_eventos(self):
        return self._fabrica_eventos