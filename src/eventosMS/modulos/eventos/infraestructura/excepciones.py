"""
Excepciones de infraestructura para el módulo de Eventos
"""

class NoExisteImplementacionParaTipoFabricaExcepcion():
    """
    Excepción lanzada cuando no existe implementación para un tipo en la fábrica
    """
    def __init__(self, tipo: str = ""):
        self.tipo = tipo
        super().__init__(f"No existe implementación para el tipo: {tipo}")
