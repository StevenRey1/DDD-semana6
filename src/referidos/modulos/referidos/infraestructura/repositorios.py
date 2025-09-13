from modulos.referidos.aplicacion.dto import ReferidoDTO
from modulos.referidos.dominio.fabricas import FabricaReferidos
from modulos.referidos.dominio.repositorio import RepositorioReferidos
from modulos.referidos.infraestructura.dto import Referido
from modulos.referidos.infraestructura.mapeadores import MapeadorReferido
from config.db import db
from uuid import UUID

class RepositorioReferidosPostgreSQL(RepositorioReferidos):
    def __init__(self):
        self._fabrica_referidos: FabricaReferidos = FabricaReferidos()

    @property
    def fabrica_referidos(self):
        return self._fabrica_referidos

    def obtener_por_id(self, id: UUID) -> Referido:
        referido_dto = db.session.query(Referido).filter_by(id=str(id)).one()
        print(f"Referido DTO from DB: {referido_dto.__dict__}")
        return self.fabrica_referidos.crear_objeto(referido_dto, MapeadorReferido())

    def obtener_todos(self) -> list[Referido]:
        # Implementar lógica para obtener todos si es necesario
        raise NotImplementedError

    def agregar(self, referido: Referido):
        print("======================")
        print("RepositorioReferidosPostgreSQL.agregar "+str(referido))
        print("======================")
        referido_dto = self.fabrica_referidos.crear_objeto(referido, MapeadorReferido())
        db.session.add(referido_dto)

    def actualizar(self, referido: Referido):
        referido_dto = self.fabrica_referidos.crear_objeto(referido, MapeadorReferido())
        db.session.merge(referido_dto) # Merge para actualizar

    def eliminar(self, referido_id: UUID):
        # Implementar lógica de eliminación si es necesario
        raise NotImplementedError
