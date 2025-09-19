from modulos.referidos.aplicacion.comandos.referido_command import ReferidoCommand, ReferidoCommandDTO
from modulos.referidos.aplicacion.handlers_comandos import HandlerReferidoCommand
from datetime import datetime
from modulos.referidos.aplicacion.mapeadores import MapeadorReferidoDTOJson
from modulos.referidos.aplicacion.queries.obtener_referido import ObtenerReferido
from modulos.referidos.aplicacion.queries.obtener_referidos_por_socio import ObtenerReferidosPorSocio
import seedwork.presentacion.api as api
import json
from flask import request, Response
from seedwork.dominio.excepciones import ExcepcionDominio

# Importaciones específicas del módulo de Referidos
from seedwork.aplicacion.comandos import ejecutar_commando
from seedwork.aplicacion.queries import ejecutar_query

# Importar el despachador para eventos de tracking
from modulos.referidos.infraestructura.despachadores import Despachador

# Creación del Blueprint para referidos
bp = api.crear_blueprint('referidos', '/')

# Endpoint para generar referido. Responde a 'POST /{idSocio}/referidos'
@bp.route('/<idSocio>/referidos', methods=('POST',))
def generar_referido(idSocio):
    """
    Endpoint: POST /{idSocio}/referidos
    Request según especificación:
    {
      "comando":"Iniciar",
      "idTransaction": "222e4567-e89b-12d3-a456-98546546544", // Opcional
      "data": {
        "idEvento": "uuid",
        "tipoEvento": "venta_creada",
        "idReferido": "123e4567-e89b-12d3-a456-426614174004",
        "monto": 150.50,
        "estado_evento": "pendiente",
        "fechaEvento": "2025-09-09T20:00:00Z"
      }
    }
    Response: HTTP 202 Accepted
    """
    try:
        payload = request.json
        print(payload)
        data_dto = ReferidoCommandDTO(
            idEvento=payload['data'].get('idEvento'),
            tipoEvento=payload['data'].get('tipoEvento'),
            idReferido=payload['data'].get('idReferido'),
            monto=payload['data'].get('monto'),
            estado_evento=payload['data'].get('estado_evento', 'pendiente'),
            fechaEvento=datetime.fromisoformat(payload['data'].get('fechaEvento').replace('Z', '+00:00')) if payload['data'].get('fechaEvento') else datetime.now()
        )
    
        comando = ReferidoCommand(
            comando="Iniciar",
            idSocio=idSocio,
            data=data_dto,
            idTransaction=payload.get('idTransaction')
        )
            
        ejecutar_commando(comando)
        
        return Response('{}', status=202, mimetype='application/json')
    except ExcepcionDominio as e:
        return Response(json.dumps(dict(error=str(e))), status=400, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps(dict(error=f"Error interno: {str(e)}")), status=500, mimetype='application/json')

@bp.route('/<idSocio>/referidos', methods=('DELETE',))
def cancelar_referido(idSocio):
    """
    Endpoint: DELETE /{idSocio}/referidos
    Request según especificación:
    {
      "comando":"Cancelar",
      "idTransaction": "222e4567-e89b-12d3-a456-98546546544", // Opcional
      "data": {
        "idEvento": "uuid",
        "tipoEvento": "venta_creada",
        "idReferido": "123e4567-e89b-12d3-a456-426614174004",
        "monto": 150.50,
        "estado_evento": "pendiente",
        "fechaEvento": "2025-09-09T20:00:00Z"
      }
    }
    Response: HTTP 202 Accepted
    """
    try:
        payload = request.json
        data_dto = ReferidoCommandDTO(
            idEvento=payload['data'].get('idEvento'),
            tipoEvento=payload['data'].get('tipoEvento'),
            idReferido=payload['data'].get('idReferido'),
            monto=payload['data'].get('monto'),
            estado_evento=payload['data'].get('estado_evento', 'pendiente'),
            fechaEvento=datetime.fromisoformat(payload['data'].get('fechaEvento').replace('Z', '+00:00')) if payload['data'].get('fechaEvento') else datetime.now()
        )
        
        comando = ReferidoCommand(
            comando="Cancelar",
            idSocio=idSocio,
            data=data_dto,
            idTransaction=payload.get('idTransaction')
        )
            
        ejecutar_commando(comando)
        
        return Response('{}', status=202, mimetype='application/json')
    except ExcepcionDominio as e:
        return Response(json.dumps(dict(error=str(e))), status=400, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps(dict(error=f"Error interno: {str(e)}")), status=500, mimetype='application/json')

# Endpoint para obtener referidos por usuario. Responde a 'GET /referidos/{idSocio}'
@bp.route('/referidos/<idSocio>', methods=('GET',))
def obtener_referidos_por_usuario(idSocio):
    """
    Endpoint: GET /referidos/{idSocio}
    Response según especificación (200):
    {
      "idSocio": "uuid",
      "referidos": [
        {  
          "idEvento": "uuid",
          "idReferido": "uuid",
          "tipoEvento": "venta_creada",
          "monto": 150.50,
          "estado": "pendiente",
          "fechaEvento": "2025-09-09T20:00:00Z",
        },
        ...
      ]
    }
    """
    try:
        # Usar la query específica para obtener referidos por socio
        query_resultado = ejecutar_query(ObtenerReferidosPorSocio(idSocio))
        
        referidos_data = query_resultado.resultado or []
        
        response_data = {
            "idSocio": idSocio,
            "referidos": []
        }
        
        for referido in referidos_data:
            referido_formatted = {
                "idEvento": str(getattr(referido, 'idEvento', '')),
                "idReferido": str(getattr(referido, 'idReferido', '')),
                "tipoEvento": getattr(referido, 'tipoEvento', ''),
                "monto": getattr(referido, 'monto', 0.0),
                "estado_evento": getattr(referido, 'estado', ''),
                "fechaEvento": str(getattr(referido, 'fechaEvento', ''))
            }
            response_data["referidos"].append(referido_formatted)
            
        return Response(json.dumps(response_data), status=200, mimetype='application/json')
            
    except ExcepcionDominio as e:
        return Response(json.dumps(dict(error=str(e))), status=400, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps(dict(error=f"Error interno: {str(e)}")), status=500, mimetype='application/json')






