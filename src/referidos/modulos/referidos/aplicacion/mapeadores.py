from seedwork.aplicacion.dto import Mapeador as AppMap
from seedwork.dominio.repositorios import Mapeador as RepMap

# Importamos las Entidades 'Referido'
from modulos.referidos.dominio.entidades import Referido
# Importamos los Objetos Valor
from modulos.referidos.dominio.objetos_valor import TipoAccion
# Importamos los DTOs de la capa de aplicación
from .dto import ReferidoDTO

from datetime import datetime
import uuid 


class MapeadorReferidoDTOJson(AppMap):
    def externo_a_dto(self, externo: dict) -> ReferidoDTO:
        referido_dto = ReferidoDTO(
            id=externo.get('id', ''),
            idSocio=externo.get('idSocio', ''),
            idReferido=externo.get('idReferido', ''),
            idEvento=externo.get('idEvento', ''),
            monto=externo.get('monto', ''),
            estado=externo.get('estado', ''),
            fechaEvento=externo.get('fechaEvento', ''),
            tipoEvento=externo.get('tipoEvento', ''),
            fecha_creacion=externo.get('fecha_creacion', ''),
            fecha_actualizacion=externo.get('fecha_actualizacion', '')
        )
        return referido_dto

    def dto_a_externo(self, dto: ReferidoDTO) -> dict:
        return {
            'id': dto.id,
            'id_afiliado': dto.id_afiliado,
            'tipo_accion': dto.tipo_accion,
            'detalle_accion': dto.detalle_accion,
            'fecha_creacion': dto.fecha_creacion,
            'fecha_actualizacion': dto.fecha_actualizacion
        }
    

class MapeadorReferido(RepMap):
    _FORMATO_FECHA = '%Y-%m-%dT%H:%M:%SZ'

    def entidad_a_dto(self, entidad: Referido) -> ReferidoDTO:
        fecha_creacion = entidad.fecha_creacion.strftime(self._FORMATO_FECHA)
        fecha_actualizacion = entidad.fecha_actualizacion.strftime(self._FORMATO_FECHA)
        _id = str(entidad.id)
        _id_afiliado = str(entidad.id_afiliado)
        referido_dto = ReferidoDTO(
            id=_id,
            id_afiliado=_id_afiliado,
            tipo_accion=entidad.tipo_accion,
            detalle_accion=entidad.detalle_accion,
            fecha_creacion=fecha_creacion,
            fecha_actualizacion=fecha_actualizacion
        )
        return referido_dto

    def dto_a_entidad(self, dto: ReferidoDTO) -> Referido:
        referido = Referido()
        referido.id = uuid.UUID(dto.id) if dto.id else uuid.uuid4()
        referido.id_afiliado = uuid.UUID(dto.id_afiliado)
        referido.tipo_accion = dto.tipo_accion
        referido.detalle_accion = dto.detalle_accion
        return referido

    def obtener_tipo(self) -> type:
        return Referido.__class__