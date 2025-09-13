""" Mapeadores para la capa de infrastructura del dominio de vuelos

En este archivo usted encontrará los diferentes mapeadores
encargados de la transformación entre formatos de dominio y DTOs

"""

import uuid
from seedwork.dominio.repositorios import Mapeador
from modulos.referidos.dominio.objetos_valor import TipoAccion
from modulos.referidos.dominio.entidades import Referido
from .dto import Referido as ReferidoDTO

class MapeadorReferido(Mapeador):
    _FORMATO_FECHA = '%Y-%m-%dT%H:%M:%SZ'

    def obtener_tipo(self) -> type:
        return Referido.__class__

    def entidad_a_dto(self, entidad: Referido) -> ReferidoDTO:
        print('=====================')
        print(f'ENTIDAD A DTO:')
        print(entidad)
        print('=====================')
        referido_dto = ReferidoDTO(
            id=str(entidad.id),
            idSocio=str(entidad.idSocio),
            idReferido=str(entidad.idReferido),
            idEvento=str(entidad.idEvento),
            monto=entidad.monto,
            estado=entidad.estado,
            fechaEvento=entidad.fechaEvento,
            tipoEvento=entidad.tipoEvento,
            fecha_creacion=entidad.fecha_creacion.strftime(self._FORMATO_FECHA),
            fecha_actualizacion=entidad.fecha_actualizacion.strftime(self._FORMATO_FECHA)
        )
        return referido_dto

    def dto_a_entidad(self, dto: ReferidoDTO) -> Referido:
        print('=====================')
        print(f'DTO A ENTIDAD: {dto}')
        print('=====================')
        referido = Referido(
            id=uuid.UUID(dto.id) if dto.id else uuid.uuid4(),
            idSocio=uuid.UUID(dto.idSocio),
            idReferido=uuid.UUID(dto.idReferido),
            idEvento=uuid.UUID(dto.idEvento),
            monto=dto.monto,
            estado=dto.estado,
            fechaEvento=dto.fechaEvento,
            tipoEvento=dto.tipoEvento
        )
        return referido