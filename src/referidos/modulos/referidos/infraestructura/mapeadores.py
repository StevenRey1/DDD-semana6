import uuid
from seedwork.dominio.repositorios import Mapeador
from modulos.referidos.dominio.entidades import Referido
from modulos.referidos.infraestructura.dto import Referido as ReferidoDTO

class MapeadorReferido(Mapeador):
    _FORMATO_FECHA = '%Y-%m-%dT%H:%M:%SZ'

    def obtener_tipo(self) -> type:
        return Referido.__class__

    def entidad_a_dto(self, entidad: Referido) -> ReferidoDTO:
        return ReferidoDTO(
            id=str(entidad.id),
            id_socio=str(entidad.id_socio),
            id_evento=str(entidad.id_evento),
            tipo_evento=entidad.tipo_evento,
            id_referido=str(entidad.id_referido),
            monto=entidad.monto,
            estado=entidad.estado,
            fecha_evento=entidad.fecha_evento
        )

    def dto_a_entidad(self, dto: ReferidoDTO) -> Referido:
        return Referido(
            id=uuid.UUID(dto.id) if dto.id else uuid.uuid4(),
            id_socio=uuid.UUID(dto.id_socio),
            id_evento=uuid.UUID(dto.id_evento),
            tipo_evento=dto.tipo_evento,
            id_referido=uuid.UUID(dto.id_referido),
            monto=dto.monto,
            estado=dto.estado,
            fecha_evento=dto.fecha_evento
        )