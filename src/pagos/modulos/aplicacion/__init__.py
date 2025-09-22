"""
Auto-registro de handlers CQRS para el módulo de Pagos.
Versión simplificada para testing.
"""

print("🚀 Cargando módulo de aplicación de Pagos...")

try:
    # NUEVO: Handler unificado según especificación
    from .comandos.pago_command_handler import PagoCommandHandler
    print("✅ PagoCommandHandler registrado")
    
    # Importar query handlers
    from .queries.obtener_estado_pago_handler import ObtenerEstadoPagoHandler
    print("✅ ObtenerEstadoPagoHandler registrado")
    
    print("🎯 Módulo de pagos cargado - Handlers CQRS esenciales registrados")
    
except ImportError as e:
    print(f"❌ Error cargando handlers: {e}")
    raise