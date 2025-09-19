from fastapi import APIRouter, status, HTTPException
from seedworks.aplicacion.comandos import ejecutar_commando
from seedworks.aplicacion.queries import ejecutar_query
from modulos.aplicacion.comandos.pago_command import PagoCommand
from modulos.aplicacion.queries.obtener_estado_pago import ObtenerEstadoPagoQuery

router = APIRouter()

# Health check endpoint
@router.get("/health")
def health_check():
    return {"status": "ok", "service": "pagos"}

@router.post("/pagos", status_code=status.HTTP_202_ACCEPTED)
def procesar_pago_command(cmd: PagoCommand):
    """
    Endpoint unificado para PagoCommand según especificación.
    Maneja comandos "Iniciar" y "Cancelar".
    """
    print(f"📥 API recibió PagoCommand: {cmd.comando} para evento {cmd.data.idEvento}")
    
    # ✅ Delegación total al sistema CQRS
    pago = ejecutar_commando(cmd)
    
    # Response HTTP 202 Accepted según especificación
    return {"message": f"Comando {cmd.comando} procesado exitosamente"}

@router.get("/pagos/{idPago}")
def obtener_estado_pago(idPago: str, idTransaction: str = None):
    """
    Endpoint para ObtenerEstadoPagoQuery según especificación.
    Response con estructura específica requerida.
    """
    print(f"📤 API consultando estado de pago: {idPago}")
    
    # ✅ Delegación total al sistema de queries  
    query = ObtenerEstadoPagoQuery(idPago=idPago, idTransaction=idTransaction)
    resultado = ejecutar_query(query)
    
    if not resultado.resultado:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    
    # Response según especificación exacta
    return resultado.resultado
