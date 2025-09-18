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

    def obtener_por_socio(self, idSocio: UUID) -> list:
        """Obtener todos los referidos de un socio específico"""
        referidos_dto = db.session.query(Referido).filter_by(idSocio=str(idSocio)).all()
        print(f"Referidos DTO from DB para socio {idSocio}: {len(referidos_dto)} encontrados")
        return [self.fabrica_referidos.crear_objeto(dto, MapeadorReferido()) for dto in referidos_dto]

    def obtener_por_id_referido(self, idReferido: UUID) -> Referido:
        """Obtener un referido específico por su idReferido"""
        referido_dto = db.session.query(Referido).filter_by(idReferido=str(idReferido)).first()
        if not referido_dto:
            raise ValueError(f"Referido no encontrado: {idReferido}")
        print(f"Referido DTO from DB by idReferido {idReferido}: {referido_dto.__dict__}")
        return self.fabrica_referidos.crear_objeto(referido_dto, MapeadorReferido())

    def obtener_por_socio_referido_evento(self, idSocio: UUID, idReferido: UUID, idEvento: UUID) -> Referido:
        referido = db.session.query(Referido).filter_by(
            idSocio=str(idSocio),
            idReferido=str(idReferido),
            idEvento=str(idEvento)
        ).first()
        print(f"💾 Referido retrieved from DB: {referido}")
        return self.fabrica_referidos.crear_objeto(referido, MapeadorReferido()) if referido else None

    def obtener_todos(self) -> list[Referido]:
        referidos_dto = db.session.query(Referido).all()
        print(f"Referidos DTO from DB: {len(referidos_dto)} encontrados")
        return [self.fabrica_referidos.crear_objeto(dto, MapeadorReferido()) for dto in referidos_dto]

    def agregar(self, referido: Referido):
        print("======================")
        print(f"💾 [REPO] RepositorioReferidosPostgreSQL.agregar - Referido: {referido}")
        print(f"💾 [REPO] ID: {referido.id}, idSocio: {referido.idSocio}, idReferido: {referido.idReferido}")
        print("======================")
        
        try:
            referido_dto = self.fabrica_referidos.crear_objeto(referido, MapeadorReferido())
            print(f"🔄 [REPO] DTO creado: {referido_dto}")
            print(f"🔄 [REPO] DTO.__dict__: {referido_dto.__dict__}")
            
            db.session.add(referido_dto)
            print("✅ [REPO] Referido agregado a la sesión de BD")
            
        except Exception as e:
            print(f"❌ [REPO] Error agregando referido: {e}")
            import traceback
            traceback.print_exc()
            raise

    def actualizar(self, referido: Referido):
        print(f"💾 [REPO] Actualizando referido: {referido}")
        referido_dto = self.fabrica_referidos.crear_objeto(referido, MapeadorReferido())
        print(f"💾 [REPO] DTO para actualizar: {referido_dto}")
        db.session.merge(referido_dto) # Merge para actualizar

    def eliminar(self, referido_id: UUID):
        # Implementar lógica de eliminación si es necesario
        raise NotImplementedError
