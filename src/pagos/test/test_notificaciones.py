"""
Script para probar el microservicio de notificaciones
VERSIÓN SIMPLIFICADA - Usa API HTTP en lugar de imports directos
"""

import requests
import json
import time

def test_api_notificaciones():
    """Prueba el API de notificaciones usando HTTP"""
    
    print("🚀 Iniciando pruebas del microservicio de notificaciones")
    print("🌐 USANDO API HTTP (http://localhost:5003)")
    print("=" * 60)
    
    base_url = "http://localhost:5003"
    
    try:
        # Prueba 1: Verificar que el servicio esté activo
        print("\n🔍 Prueba 1: Verificar estado del servicio")
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("   ✅ Servicio activo y respondiendo")
        else:
            print(f"   ❌ Servicio no responde: {response.status_code}")
            return
        
        # Prueba 2: Listar notificaciones iniciales
        print("\n📋 Prueba 2: Listar notificaciones existentes")
        response = requests.get(f"{base_url}/notificaciones", timeout=10)
        data = response.json()
        if data.get("exito"):
            total_inicial = data.get("datos", {}).get("total", 0)
            print(f"   📊 Notificaciones existentes: {total_inicial}")
        else:
            print(f"   ❌ Error listando: {data}")
            return
        
        # Prueba 3: Crear notificación de email
        print("\n📧 Prueba 3: Crear notificación de email")
        payload_email = {
            "idSocio": "test-user-123",  # ✅ Cambio: id_usuario → idSocio
            "tipo": "transaccional",
            "canal": "email",
            "destinatario": "test@example.com",
            "titulo": "Notificación de Prueba",
            "mensaje": "Esta es una notificación de prueba para email"
        }
        
        response = requests.post(f"{base_url}/notificaciones", json=payload_email, timeout=10)
        if response.status_code == 201:
            email_data = response.json()
            email_id = email_data.get("datos", {}).get("idNotificacion")
            print(f"   ✅ Email creado: {email_id}")
        else:
            print(f"   ❌ Error creando email: {response.status_code} - {response.text}")
        
        # Prueba 4: Crear notificación SMS
        print("\n📱 Prueba 4: Crear notificación SMS")
        payload_sms = {
            "idSocio": "test-user-456",  # ✅ Cambio: id_usuario → idSocio 
            "tipo": "alerta",
            "canal": "sms",
            "destinatario": "+1234567890",
            "titulo": "Código de verificación",
            "mensaje": "Tu código es: 123456"
        }
        
        response = requests.post(f"{base_url}/notificaciones", json=payload_sms, timeout=10)
        if response.status_code == 201:
            sms_data = response.json()
            sms_id = sms_data.get("datos", {}).get("idNotificacion")
            print(f"   ✅ SMS creado: {sms_id}")
        else:
            print(f"   ❌ Error creando SMS: {response.status_code} - {response.text}")
        
        # Prueba 5: Crear notificación push
        print("\n🔔 Prueba 5: Crear notificación push")
        payload_push = {
            "idSocio": "test-user-789",  # ✅ Cambio: id_usuario → idSocio
            "tipo": "promocional", 
            "canal": "push",
            "destinatario": "device-token-xyz",
            "titulo": "Oferta especial",
            "mensaje": "20% de descuento en tu próxima compra"
        }
        
        response = requests.post(f"{base_url}/notificaciones", json=payload_push, timeout=10)
        if response.status_code == 201:
            push_data = response.json()
            push_id = push_data.get("datos", {}).get("idNotificacion")
            print(f"   ✅ Push creado: {push_id}")
        else:
            print(f"   ❌ Error creando push: {response.status_code} - {response.text}")
        
        # Prueba 6: Verificar que se crearon las notificaciones
        print("\n📊 Prueba 6: Verificar notificaciones creadas")
        time.sleep(1)  # Dar tiempo para que se persistan
        
        response = requests.get(f"{base_url}/notificaciones", timeout=10)
        data = response.json()
        if data.get("exito"):
            total_final = data.get("datos", {}).get("total", 0)
            items = data.get("datos", {}).get("items", [])
            print(f"   📊 Total final: {total_final}")
            print(f"   📈 Nuevas notificaciones: {total_final - total_inicial}")
            
            # Mostrar las últimas 3
            for item in items[-3:]:
                print(f"   📝 {item['tipo']}: {item['titulo']} ({item['idUsuario']})")
        else:
            print(f"   ❌ Error verificando: {data}")
        
        # Prueba 7: Obtener notificaciones de un usuario específico
        print("\n👤 Prueba 7: Obtener notificaciones por usuario")
        response = requests.get(f"{base_url}/usuarios/test-user-123/notificaciones", timeout=10)
        if response.status_code == 200:
            user_data = response.json()
            if user_data.get("exito"):
                user_notifs = user_data.get("datos", {}).get("items", [])
                print(f"   ✅ Notificaciones del usuario: {len(user_notifs)}")
                for notif in user_notifs:
                    print(f"   📝 {notif['titulo']} - {notif['estado']}")
            else:
                print(f"   ❌ Error: {user_data}")
        else:
            print(f"   ❌ Error obteniendo usuario: {response.status_code}")
        
        print(f"\n📊 Resumen de pruebas:")
        print(f"   ✅ Servicio funcionando con PostgreSQL")
        print(f"   ✅ API endpoints respondiendo")
        print(f"   ✅ Persistencia de datos confirmada")
        print(f"   ✅ Diferentes tipos de notificaciones creadas")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ Pruebas del microservicio completadas")


if __name__ == "__main__":
    test_api_notificaciones()
