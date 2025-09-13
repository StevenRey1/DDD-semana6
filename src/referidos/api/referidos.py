from modulos.referidos.aplicacion.comandos.crear_referido import CrearReferido
from modulos.referidos.aplicacion.mapeadores import MapeadorReferidoDTOJson
from modulos.referidos.aplicacion.queries.obtener_referido import ObtenerReferido
import seedwork.presentacion.api as api
import json
from flask import request, Response
from seedwork.dominio.excepciones import ExcepcionDominio

# Importaciones específicas del módulo de Pagos
from seedwork.aplicacion.comandos import ejecutar_commando
from seedwork.aplicacion.queries import ejecutar_query

# Creación del Blueprint. La URL base para todas las rutas en este archivo será '/pagos'
bp = api.crear_blueprint('referidos', '/referidos')

# Endpoint para crear un pago. Responde a 'POST /pagos/'
@bp.route('/', methods=('POST',))
def crear_referido():
    try:
        referido_dict = request.json
        map_referido = MapeadorReferidoDTOJson()
        referido_dto = map_referido.externo_a_dto(referido_dict)
        
        comando = CrearReferido(
            idSocio=referido_dto.idSocio,
            idReferido=referido_dto.idReferido,
            idEvento=referido_dto.idEvento,
            monto=referido_dto.monto,
            estado=referido_dto.estado,
            fechaEvento=referido_dto.fechaEvento,
            tipoEvento=referido_dto.tipoEvento,
            fecha_creacion=referido_dto.fecha_creacion,
            fecha_actualizacion=referido_dto.fecha_actualizacion
        )
            
        ejecutar_commando(comando)
        
        return Response('{}', status=202, mimetype='application/json')
    except ExcepcionDominio as e:
        return Response(json.dumps(dict(error=str(e))), status=400, mimetype='application/json')

# Endpoint para obtener un pago. Responde a 'GET /pagos/<id>'
@bp.route('/<id>', methods=('GET',))
def dar_referido(id=None):
    if id:
        query_resultado = ejecutar_query(ObtenerReferido(id))
        map_referido = MapeadorReferidoDTOJson()
        return map_referido.dto_a_externo(query_resultado.resultado)
    else:
        # Esto podría devolver una lista de todos los pagos o un error
        return Response(json.dumps(dict(error="Se requiere un ID de referido")), status=400, mimetype='application/json')
