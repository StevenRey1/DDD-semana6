from seedworks.aplicacion.queries import ejecutar_query, QueryResultado
from .base import PagoQueryBaseHandler
from .obtener_estado_pago import ObtenerEstadoPagoQuery
from ...infraestructura.repositorio_postgresql import RepositorioPagosPG
from config.pulsar_config import Settings

class ObtenerEstadoPagoHandler(PagoQueryBaseHandler):
    """
    Handler que obtiene el estado actual de un pago.
    Response según especificación con idTransaction y campos renombrados.
    """
    
    def handle(self, query: ObtenerEstadoPagoQuery) -> QueryResultado:
        print(f"🔍 Ejecutando ObtenerEstadoPagoHandler para pago: {query.idPago}")
        
        settings = Settings()
        repo = RepositorioPagosPG(settings.DB_URL)
        
        with repo.SessionLocal() as session:
            # Buscar pago por ID
            pago = session.query(repo.PagoORM).filter_by(idPago=query.idPago).first()
            
            if not pago:
                print(f"❌ Pago {query.idPago} no encontrado")
                return QueryResultado(resultado=None)
            
            # Response según especificación
            pago_response = {
                "idTransaction": query.idTransaction,  # Viene del query
                "idPago": pago.idPago,
                "idSocio": pago.idSocio,
                "pago": float(pago.monto),  # Campo renombrado de 'monto' a 'pago'
                "estado_pago": pago.estado,  # Campo renombrado
                "fechaPago": pago.fechaPago.isoformat()
            }
            
            print(f"✅ Pago {query.idPago} encontrado: {pago_response['estado_pago']}")
            return QueryResultado(resultado=pago_response)

# Registrar handler usando singledispatch
@ejecutar_query.register(ObtenerEstadoPagoQuery)
def ejecutar_query_obtener_estado_pago(query: ObtenerEstadoPagoQuery):
    handler = ObtenerEstadoPagoHandler()
    return handler.handle(query)