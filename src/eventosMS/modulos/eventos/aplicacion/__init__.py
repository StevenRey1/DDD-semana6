from pydispatch import dispatcher
from .handlers import HandlerEventoIntegracion
from ..dominio.eventos import EventoRegistrado

# Conectar handlers de integración para eventos de notificaciones
dispatcher.connect(HandlerEventoIntegracion.handle_evento_registrado, signal=f'{EventoRegistrado.__name__}Integracion')

# Conectar handlers para eventos de pagos (estos escuchan eventos externos)
# Nota: Los eventos de pagos se manejan vía Pulsar, no pydispatch
print("✅ Módulo de eventos cargado - Handlers registrados")
