from flask import jsonify, request, Response, json
from modulos.referidos.aplicacion.comandos.generar_referido import GenerarReferido
from modulos.referidos.aplicacion.mapeadores import MapeadorReferidoDTOJson
from modulos.referidos.aplicacion.queries.obtener_referidos_por_usuario import ObtenerReferidosPorUsuario
import seedwork.presentacion.api as api
from seedwork.dominio.excepciones import ExcepcionDominio
from seedwork.aplicacion.comandos import ejecutar_commando
from seedwork.aplicacion.queries import ejecutar_query

bp = api.crear_blueprint('referidos', '')

@bp.route('/<string:idSocio>/referidos', methods=['POST'])
def generar_referido(idSocio=None):
    try:
        referido_dict = request.json
        referido_dict['idSocio'] = idSocio

        map_referido = MapeadorReferidoDTOJson()
        referido_dto = map_referido.externo_a_dto(referido_dict)

        comando = GenerarReferido(
            idSocio=referido_dto.idSocio,
            idEvento=referido_dto.idEvento,
            tipoEvento=referido_dto.tipoEvento,
            idReferido=referido_dto.idReferido,
            monto=referido_dto.monto,
            estado=referido_dto.estado,
            fechaEvento=referido_dto.fechaEvento
        )
        
        ejecutar_commando(comando)
        
        return Response('{}', status=202, mimetype='application/json')
    except ExcepcionDominio as e:
        return Response(json.dumps(dict(error=str(e))), status=400, mimetype='application/json')

@bp.route('/referidos/<string:idSocio>', methods=['GET'])
def obtener_referidos_por_usuario(idSocio=None):
    if idSocio:
        query_resultado = ejecutar_query(ObtenerReferidosPorUsuario(idSocio))
        # The query_resultado.resultado is already a dictionary with 'idSocio' and 'referidos'
        # where 'referidos' is a list of dictionaries (external representation).
        # So, we can directly return it as JSON.
        return jsonify(query_resultado.resultado)
    else:
        return Response(json.dumps(dict(error="Se requiere un ID de socio")), status=400, mimetype='application/json')