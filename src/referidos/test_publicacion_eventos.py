"""
Script para probar la publicación de eventos VentaReferidaConfirmada y VentaReferidaRechazada
usando el Despachador centralizado
"""
import sys
import os
sys.path.append('/app/src/referidos')

from modulos.referidos.infraestructura.despachadores import Despachador

def probar_publicacion_confirmacion():
    """Probar publicación de VentaReferidaConfirmada"""
    print("🧪 Probando publicación de VentaReferidaConfirmada...")
    
    try:
        despachador = Despachador()
        
        # Datos de prueba para confirmación
        datos_confirmacion = {
            "idReferido": "conf-123-test",
            "idSocio": "socio-test-456", 
            "montoComision": 175.50,
            "fechaConfirmacion": "2025-09-13T23:25:00Z"
        }
        
        despachador.publicar_venta_confirmada(datos_confirmacion)
        print("✅ VentaReferidaConfirmada publicada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error publicando VentaReferidaConfirmada: {e}")

def probar_publicacion_rechazo():
    """Probar publicación de VentaReferidaRechazada"""
    print("🧪 Probando publicación de VentaReferidaRechazada...")
    
    try:
        despachador = Despachador()
        
        # Datos de prueba para rechazo
        datos_rechazo = {
            "idReferido": "rech-789-test",
            "idSocio": "socio-test-456",
            "motivo": "Cliente no cumple requisitos", 
            "fechaRechazo": "2025-09-13T23:28:00Z"
        }
        
        despachador.publicar_venta_rechazada(datos_rechazo)
        print("✅ VentaReferidaRechazada publicada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error publicando VentaReferidaRechazada: {e}")

def main():
    """Función principal para ejecutar todas las pruebas"""
    print("🚀 Iniciando pruebas de publicación de eventos...")
    print("=" * 60)
    
    # Probar publicación de confirmación
    probar_publicacion_confirmacion()
    print("-" * 40)
    
    # Probar publicación de rechazo  
    probar_publicacion_rechazo()
    
    print("=" * 60)
    print("✅ Pruebas de publicación completadas!")

if __name__ == "__main__":
    main()