from modulos.referidos.aplicacion.comandos.generar_referido import GenerarReferidoCommand
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
        "idEvento": "uuid",
        "tipoEvento": "venta_creada",
        "idReferido": "123e4567-e89b-12d3-a456-426614174004",
        "monto": 150.50,
        "estado": "pendiente",
        "fechaEvento": "2025-09-09T20:00:00Z"
    }
    Response: HTTP 202 Accepted
    """
    try:
        referido_dict = request.json
        
        # Crear comando con la estructura específica
        comando = GenerarReferidoCommand(
            idEvento=referido_dict.get('idEvento'),
            tipoEvento=referido_dict.get('tipoEvento'),
            idReferido=referido_dict.get('idReferido'),
            idSocio=idSocio,  # Del path parameter
            monto=referido_dict.get('monto'),
            estado=referido_dict.get('estado', 'pendiente'),  # Default pendiente
            fechaEvento=referido_dict.get('fechaEvento')
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
                "estado": getattr(referido, 'estado', ''),
                "fechaEvento": str(getattr(referido, 'fechaEvento', ''))
            }
            response_data["referidos"].append(referido_formatted)
            
        return Response(json.dumps(response_data), status=200, mimetype='application/json')
            
    except ExcepcionDominio as e:
        return Response(json.dumps(dict(error=str(e))), status=400, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps(dict(error=f"Error interno: {str(e)}")), status=500, mimetype='application/json')


# Endpoint para confirmar venta de referido. Responde a 'POST /referidos/{idReferido}/confirmar'
@bp.route('/referidos/<idReferido>/confirmar', methods=('POST',))
def confirmar_venta_referido(idReferido):
    """
    Endpoint: POST /referidos/{idReferido}/confirmar
    Request:
    {
        "monto": 25.75,
        "fechaConfirmacion": "2025-09-10T15:30:00Z"
    }
    Response: HTTP 200 OK
    """
    try:
        data = request.json
        print(f"🔄 [API] Confirmando referido {idReferido} con data: {data}")
        
        # Obtener el referido existente para conseguir el idSocio
        from seedwork.infraestructura.uow import UnidadTrabajoPuerto
        repositorio = UnidadTrabajoPuerto().repositorio_referidos()
        referido = repositorio.obtener_por_id_referido(idReferido)
        
        print(f"🔄 [API] Referido encontrado: idSocio={referido.idSocio}, idReferido={referido.idReferido}")
        
        # Crear instancia del despachador
        despachador = Despachador()
        
        # Publicar evento VentaReferidaConfirmada con todos los datos necesarios
        despachador.publicar_venta_confirmada({
            'idReferido': idReferido,
            'idSocio': str(referido.idSocio),  # Obtenido de la BD
            'monto': data.get('monto'),  # Pasar monto directamente
            'fechaEvento': data.get('fechaEvento')
        })
        
        return Response('{"status": "confirmado"}', status=200, mimetype='application/json')
        
    except ExcepcionDominio as e:
        return Response(json.dumps(dict(error=str(e))), status=400, mimetype='application/json')
    except Exception as e:
        print(f"❌ [API] Error confirmando referido: {e}")
        import traceback
        traceback.print_exc()
        return Response(json.dumps(dict(error=f"Error interno: {str(e)}")), status=500, mimetype='application/json')


# Endpoint para rechazar venta de referido. Responde a 'POST /referidos/{idReferido}/rechazar'
@bp.route('/referidos/<idReferido>/rechazar', methods=('POST',))
def rechazar_venta_referido(idReferido):
    """
    Endpoint: POST /referidos/{idReferido}/rechazar
    Request:
    {
        "idSocio": "uuid",
        "motivo": "Cliente no califica",
        "fechaRechazo": "2025-09-10T15:30:00Z"
    }
    Response: HTTP 200 OK
    """
    try:
        data = request.json
        
        # Crear instancia del despachador
        despachador = Despachador()
        
        # Publicar evento VentaReferidaRechazada
        despachador.publicar_venta_rechazada({
            'idReferido': idReferido,
            'idSocio': data.get('idSocio'),
            'motivo': data.get('motivo'),
            'fechaRechazo': data.get('fechaRechazo')
        })
        
        return Response('{"status": "rechazado"}', status=200, mimetype='application/json')
        
    except ExcepcionDominio as e:
        return Response(json.dumps(dict(error=str(e))), status=400, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps(dict(error=f"Error interno: {str(e)}")), status=500, mimetype='application/json')
