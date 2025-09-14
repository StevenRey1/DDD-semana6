from seedwork.aplicacion.dto import Mapeador as AppMap
from modulos.referidos.aplicacion.dto import ReferidoDTO
from modulos.referidos.infraestructura.dto import Referido as ReferidoInfra

class MapeadorReferidoDTOJson(AppMap):
    def externo_a_dto(self, externo: dict) -> ReferidoDTO:
        return ReferidoDTO(
            idSocio=externo.get('idSocio'),
            idEvento=externo.get('idEvento'),
            tipoEvento=externo.get('tipoEvento'),
            idReferido=externo.get('idReferido'),
            monto=externo.get('monto'),
            estado=externo.get('estado'),
            fechaEvento=externo.get('fechaEvento')
        )

    def dto_a_externo(self, dto: any) -> dict:
        if not dto:
            return {}
        
        # Handle ReferidoDTO (application DTO) or ReferidoInfra (infrastructure DTO/model)
        if isinstance(dto, ReferidoDTO):
            return {
                'idSocio': dto.idSocio,
                'idEvento': dto.idEvento,
                'tipoEvento': dto.tipoEvento,
                'idReferido': dto.idReferido,
                'monto': dto.monto,
                'estado': dto.estado,
                'fechaEvento': dto.fechaEvento
            }
        elif isinstance(dto, ReferidoInfra):
            return {
                'idSocio': dto.id_socio,
                'idEvento': dto.id_evento,
                'tipoEvento': dto.tipo_evento,
                'idReferido': dto.id_referido,
                'monto': dto.monto,
                'estado': dto.estado,
                'fechaEvento': str(dto.fecha_evento) # Convert datetime to string
            }
        else:
            return {}
