# Propósito: Clase base para los handlers de comandos de referidos, para 
# inyectar dependencias comunes.

from modulos.referidos.dominio.fabricas import FabricaReferidos
from seedwork.aplicacion.comandos import ComandoHandler
from modulos.referidos.infraestructura.fabricas import FabricaRepositorio

class CrearReferidoBaseHandler(ComandoHandler):
    def __init__(self):
        self._fabrica_repositorio: FabricaRepositorio = FabricaRepositorio()
        self._fabrica_referidos: FabricaReferidos = FabricaReferidos()

    @property
    def fabrica_repositorio(self):
        return self._fabrica_repositorio
    
    @property
    def fabrica_referidos(self):
        return self._fabrica_referidos