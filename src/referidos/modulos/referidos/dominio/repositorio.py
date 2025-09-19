from abc import ABC, abstractmethod
from uuid import UUID
from seedwork.dominio.repositorios import Repositorio

class RepositorioReferidos(Repositorio, ABC):
    
    @abstractmethod
    def obtener_por_socio(self, idSocio: UUID) -> list:
        ...
    
    @abstractmethod
    def obtener_por_id_referido(self, idReferido: UUID):
        ...

    @abstractmethod
    def obtener_por_socio_referido_evento(self, idSocio: UUID, idReferido: UUID, idEvento: UUID):
        ...