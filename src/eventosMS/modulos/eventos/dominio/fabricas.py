"""
Fábricas del dominio de Eventos
"""
from dataclasses import dataclass
from typing import List

from modulos.eventos.dominio.excepciones import TipoObjetoNoExisteEnDominioEventosExcepcion
from modulos.eventos.dominio.reglas import MontoDebeSerPositivo
from seedwork.dominio.entidades import Entidad
from seedwork.dominio.repositorios import Mapeador
from .entidades import Evento
from seedwork.dominio.fabricas import Fabrica

@dataclass
class _FabricaEvento(Fabrica):
    def crear_objeto(self, obj: any, mapeador: Mapeador) -> any:
        if isinstance(obj, Entidad):
            return mapeador.entidad_a_dto(obj)
        
        else:
            evento: Evento = mapeador.dto_a_entidad(obj)

            # Validación de reglas de negocio
            self.validar_regla(MontoDebeSerPositivo(evento.monto))

            return evento

@dataclass
class _FabricaListaEventos(Fabrica):
    def crear_objeto(self, obj_lista: List[any], mapeador: Mapeador) -> List[Evento]:
        """
        Crea una lista de objetos Evento usando el mapeador
        """
        if not isinstance(obj_lista, list):
            raise ValueError("El objeto debe ser una lista")
        
        eventos = []
        fabrica_evento = _FabricaEvento()
        
        for obj in obj_lista:
            try:
                if isinstance(obj, Entidad):
                    # Si es una entidad, convertir a DTO
                    evento_dto = mapeador.entidad_a_dto(obj)
                    eventos.append(evento_dto)
                else:
                    # Si es un DTO, convertir a entidad
                    evento: Evento = fabrica_evento.crear_objeto(obj, mapeador)
                    eventos.append(evento)
                    
            except Exception as e:
                # Log del error pero continuar con los otros elementos
                print(f"Error procesando elemento de la lista: {e}")
                continue
        
        return eventos

@dataclass
class FabricaEventos(Fabrica):
    def crear_objeto(self, obj: any, mapeador: Mapeador) -> any:
        if mapeador.obtener_tipo() == Evento.__class__:
            fabrica_evento = _FabricaEvento()
            return fabrica_evento.crear_objeto(obj, mapeador)
        else:
            raise TipoObjetoNoExisteEnDominioEventosExcepcion()
    
    def crear_lista_eventos(self, obj_lista: List[any], mapeador: Mapeador) -> List[Evento]:
        """
        Método específico para crear listas de eventos
        """
        fabrica_lista = _FabricaListaEventos()
        return fabrica_lista.crear_objeto(obj_lista, mapeador)