import seedwork.presentacion.api as api
import json
from flask import request, Response
from seedwork.dominio.excepciones import ExcepcionDominio

# Importaciones específicas del módulo de Eventos
from modulos.eventos.aplicacion.mapeadores import MapeadorEventoDTOJson
from modulos.eventos.aplicacion.comandos.crear_evento import CrearEvento
from modulos.eventos.aplicacion.queries.obtener_eventos_socio import ObtenerEventosSocio
from seedwork.aplicacion.comandos import ejecutar_commando
from seedwork.aplicacion.queries import ejecutar_query

# Creación del Blueprint. La URL base para todas las rutas en este archivo será '/eventos'
bp = api.crear_blueprint('eventos', '/eventos')

@bp.route('/', methods=('POST',))
def crear_evento():
    try:
        evento_dict = request.json
        map_evento = MapeadorEventoDTOJson()
        evento_dto = map_evento.externo_a_dto(evento_dict)

        comando = CrearEvento(
            tipo=evento_dto.tipo,
            id_socio=evento_dto.id_socio,
            id_referido=evento_dto.id_referido,
            monto=evento_dto.monto,
            fecha_evento=evento_dto.fecha_evento,
            comando=evento_dto.comando,
            id_transaction=evento_dto.id_transaction
        )
        
        ejecutar_commando(comando)
        
        return Response('{}', status=202, mimetype='application/json')
    except ExcepcionDominio as e:
        return Response(json.dumps(dict(error=str(e))), status=400, mimetype='application/json')

@bp.route('/<id_socio>', methods=('GET',))
def dar_eventos_socio_usando_query(id_socio=None):
    if id_socio:
        query_resultado = ejecutar_query(ObtenerEventosSocio(id_socio))
        map_evento = MapeadorEventoDTOJson()

        return map_evento.lista_dto_a_externo(query_resultado.resultado)
    else:
        # Esto podría devolver una lista de todos los eventos o un error
        return Response(json.dumps({"error": "Se requiere un ID de evento"}), status=400, mimetype='application/json')


@bp.route('/sagas/<nombre>/<correlacion_id>', methods=('GET',))
def obtener_saga(nombre, correlacion_id):
    """Endpoint pedagógico para consultar estado de una saga y su log de pasos."""
    try:
        from modulos.sagas.infraestructura.repositorio_saga import RepositorioSaga
        repo = RepositorioSaga()
        instancia = repo.obtener_por_correlacion(nombre, correlacion_id)
        if not instancia:
            return Response(json.dumps({"error": "Saga no encontrada"}), status=404, mimetype='application/json')

        pasos = repo.listar_pasos(instancia.id)
        respuesta = {
            "nombre": instancia.nombre,
            "correlacionId": instancia.correlacion_id,
            "estado": instancia.estado,
            "pasoActual": instancia.paso_actual,
            "totalPasos": instancia.total_pasos,
            "iniciadaEn": instancia.iniciada_en.isoformat() if instancia.iniciada_en else None,
            "finalizadaEn": instancia.finalizada_en.isoformat() if instancia.finalizada_en else None,
            "steps": [
                {
                    "paso": s.paso,
                    "nombrePaso": s.nombre_paso,
                    "accion": s.accion,
                    "estado": s.estado,
                    "detalle": s.detalle,
                    "timestamp": s.timestamp.isoformat() if s.timestamp else None
                } for s in pasos
            ]
        }
        return Response(json.dumps(respuesta), status=200, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), status=500, mimetype='application/json')