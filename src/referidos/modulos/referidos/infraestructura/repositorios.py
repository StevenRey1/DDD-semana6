from modulos.referidos.dominio.fabricas import FabricaReferidos
from modulos.referidos.dominio.repositorio import RepositorioReferidos
from modulos.referidos.infraestructura.dto import Referido as ReferidoInfra
from modulos.referidos.infraestructura.mapeadores import MapeadorReferido
from config.db import db
from uuid import UUID

class RepositorioReferidosPostgreSQL(RepositorioReferidos):
    def __init__(self):
        self._fabrica_referidos: FabricaReferidos = FabricaReferidos()

    @property
    def fabrica_referidos(self):
        return self._fabrica_referidos

    def obtener_por_id(self, id: UUID) -> ReferidoInfra:
        # Implementar lógica para obtener un referido por ID si es necesario
        raise NotImplementedError

    def obtener_todos(self) -> list[ReferidoInfra]:
        # Implementar lógica para obtener todos si es necesario
        raise NotImplementedError

    def agregar(self, referido: ReferidoInfra):
        print(f"DEBUG: Inside RepositorioReferidosPostgreSQL.agregar - Adding referido to session: {referido}")
        db.session.add(referido)
        print(f"DEBUG: Referido added to session: {referido}")

    def actualizar(self, referido: ReferidoInfra):
        db.session.merge(referido)

    def eliminar(self, referido_id: UUID):
        # Implementar lógica de eliminación si es necesario
        raise NotImplementedError

    def obtener_por_socio_id(self, id_socio: UUID) -> list[ReferidoInfra]:
        return db.session.query(ReferidoInfra).filter_by(id_socio=str(id_socio)).all()