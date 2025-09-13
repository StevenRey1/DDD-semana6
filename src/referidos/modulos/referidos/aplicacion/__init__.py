from pydispatch import dispatcher
from .handlers import HandlerReferidosIntegracion
from modulos.referidos.dominio.eventos import ReferidoCreado, ReferidoConfirmado

# --- ¡ESTA ES LA CORRECCIÓN CLAVE! ---
# La Unit of Work emite la señal con el sufijo 'Integracion' DESPUÉS del commit.
# El handler de integración debe escuchar esta señal específica.

dispatcher.connect(HandlerReferidosIntegracion.handle_referido_creado, signal=f'{ReferidoCreado.__name__}Integracion')
dispatcher.connect(HandlerReferidosIntegracion.handle_referido_confirmado, signal=f'{ReferidoConfirmado.__name__}Integracion')
