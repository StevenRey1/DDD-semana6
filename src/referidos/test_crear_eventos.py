"""
Script para probar solo la creación de eventos sin conectar a Pulsar
"""
import sys
sys.path.append('/app/src/referidos')

from modulos.referidos.infraestructura.schema.v1.eventos_tracking import VentaReferidaConfirmada, VentaReferidaRechazada

def test_crear_evento_confirmado():
    """Test para crear evento VentaReferidaConfirmada"""
    print("🧪 Probando creación de VentaReferidaConfirmada...")
    
    try:
        evento = VentaReferidaConfirmada(
            idEvento="conf-123-test",
            idSocio="socio-test-456",
            monto=175.50,
            fechaEvento="2025-09-13T23:25:00Z"
        )
        
        print(f"✅ VentaReferidaConfirmada creada exitosamente:")
        print(f"   - idEvento: {evento.idEvento}")
        print(f"   - idSocio: {evento.idSocio}")
        print(f"   - monto: {evento.monto}")
        print(f"   - fechaEvento: {evento.fechaEvento}")
        
    except Exception as e:
        print(f"❌ Error creando VentaReferidaConfirmada: {e}")

def test_crear_evento_rechazado():
    """Test para crear evento VentaReferidaRechazada"""
    print("🧪 Probando creación de VentaReferidaRechazada...")
    
    try:
        evento = VentaReferidaRechazada(
            idEvento="rech-789-test",
            idSocio="socio-test-456",
            monto=0.0,
            razon="Cliente no cumple requisitos",
            fechaEvento="2025-09-13T23:28:00Z"
        )
        
        print(f"✅ VentaReferidaRechazada creada exitosamente:")
        print(f"   - idEvento: {evento.idEvento}")
        print(f"   - idSocio: {evento.idSocio}")
        print(f"   - monto: {evento.monto}")
        print(f"   - razon: {evento.razon}")
        print(f"   - fechaEvento: {evento.fechaEvento}")
        
    except Exception as e:
        print(f"❌ Error creando VentaReferidaRechazada: {e}")

def main():
    """Función principal"""
    print("🚀 Iniciando pruebas de creación de eventos...")
    print("=" * 60)
    
    test_crear_evento_confirmado()
    print("-" * 40)
    test_crear_evento_rechazado()
    
    print("=" * 60)
    print("✅ Pruebas de creación completadas!")

if __name__ == "__main__":
    main()