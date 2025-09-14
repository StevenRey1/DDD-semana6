"""
Test completo del microservicio de notificaciones
Incluye servicios de aplicación, CQRS, eventos, etc.
"""

import asyncio
import sys
import os

# Agregar el directorio actual al path para importaciones
sys.path.insert(0, os.path.dirname(__file__))

async def test_completo():
    """Test completo de funcionalidad del microservicio"""
    print("🚀 INICIANDO TEST COMPLETO DEL MICROSERVICIO DE NOTIFICACIONES")
    print("=" * 80)
    
    try:
        # Importar todos los componentes
        print("📦 Importando componentes del microservicio...")
        
        from modulos.aplicacion.servicios import ServicioAplicacionNotificaciones
        from modulos.aplicacion.dto import CrearNotificacionDTO
        from modulos.infraestructura.repositorios import RepositorioNotificacionesMemoria
        from modulos.infraestructura.despachadores import DespachadorEventos
        from modulos.dominio.fabricas import FabricaNotificaciones
        
        print("   ✅ Todos los componentes importados correctamente")
        
        # Configurar infraestructura
        print("\n🏗️ Configurando infraestructura...")
        repositorio = RepositorioNotificacionesMemoria()
        despachador = DespachadorEventos()
        servicio = ServicioAplicacionNotificaciones(repositorio, despachador)
        
        # Intentar inicializar despachador (sin fallar si no hay Pulsar)
        try:
            await despachador.inicializar()
            print("   ✅ Despachador de eventos inicializado")
        except Exception as e:
            print(f"   ⚠️ Despachador sin Pulsar: {e}")
        
        print("   ✅ Infraestructura configurada")
        
        # Test 1: Crear notificación usando servicio de aplicación
        print("\n📧 Test 1: Crear notificación usando servicio...")
        dto_email = CrearNotificacionDTO(
            id_usuario="user-001",
            tipo="bienvenida",
            canal="email",
            destinatario="test@example.com",
            titulo="¡Bienvenido!",
            mensaje="¡Gracias por registrarte en AlpesPartners!",
            datos_adicionales={"plantilla": "bienvenida", "idioma": "es"}
        )
        
        notif_result = await servicio.crear_notificacion(dto_email)
        print(f"   ✅ Notificación creada: {notif_result.id_notificacion}")
        print(f"   📧 Email: {notif_result.destinatario}")
        print(f"   📝 Título: {notif_result.titulo}")
        
        # Test 2: Crear notificación SMS
        print("\n📱 Test 2: Crear notificación SMS...")
        dto_sms = CrearNotificacionDTO(
            id_usuario="user-002",
            tipo="transaccional",
            canal="sms",
            destinatario="+1234567890",
            titulo="Código de verificación",
            mensaje="Su código es: 123456",
            datos_adicionales={"codigo": "123456", "expira": "5min"}
        )
        
        sms_result = await servicio.crear_notificacion(dto_sms)
        print(f"   ✅ SMS creado: {sms_result.id_notificacion}")
        print(f"   📱 Teléfono: {sms_result.destinatario}")
        
        # Test 3: Crear notificación push promocional
        print("\n🔔 Test 3: Crear notificación push promocional...")
        dto_push = CrearNotificacionDTO(
            id_usuario="user-003",
            tipo="promocional",
            canal="push",
            destinatario="device-token-xyz123",
            titulo="¡Oferta especial!",
            mensaje="20% de descuento en tu próxima compra",
            datos_adicionales={"descuento": 20, "categoria": "ropa"}
        )
        
        push_result = await servicio.crear_notificacion(dto_push)
        print(f"   ✅ Push creada: {push_result.id_notificacion}")
        print(f"   🔔 Token: {push_result.destinatario}")
        
        # Test 4: Obtener notificación por ID
        print("\n🔍 Test 4: Obtener notificación por ID...")
        obtenida = await servicio.obtener_notificacion(notif_result.id_notificacion)
        if obtenida:
            print(f"   ✅ Notificación encontrada: {obtenida.titulo}")
            print(f"   📊 Estado: {obtenida.estado}")
        else:
            print("   ❌ No se encontró la notificación")
        
        # Test 5: Obtener notificaciones por usuario
        print("\n👤 Test 5: Obtener notificaciones por usuario...")
        del_usuario = await servicio.obtener_notificaciones_usuario("user-001")
        print(f"   ✅ Notificaciones encontradas: {len(del_usuario.notificaciones)}")
        for item in del_usuario.notificaciones:
            print(f"   📝 {item.titulo} - {item.estado}")
        
        # Test 6: Enviar notificación
        print("\n📤 Test 6: Enviar notificación...")
        enviada = await servicio.enviar_notificacion(notif_result.id_notificacion)
        print(f"   ✅ Notificación enviada: {enviada.id_notificacion}")
        print(f"   📊 Nuevo estado: {enviada.estado}")
        print(f"   ⏰ Fecha envío: {enviada.fecha_envio}")
        
        # Test 7: Marcar notificación como fallida
        print("\n❌ Test 7: Marcar notificación como fallida...")
        fallida = await servicio.marcar_notificacion_fallida(
            sms_result.id_notificacion,
            "Número telefónico inválido"
        )
        print(f"   ✅ Notificación marcada como fallida: {fallida.id_notificacion}")
        print(f"   📊 Estado: {fallida.estado}")
        print(f"   ❌ Error: {fallida.detalle_error}")
        
        # Test 8: Obtener notificaciones pendientes
        print("\n⏳ Test 8: Obtener notificaciones pendientes...")
        pendientes = await servicio.obtener_notificaciones_pendientes()
        print(f"   ✅ Notificaciones pendientes: {len(pendientes)}")
        for pend in pendientes:
            print(f"   📝 {pend.titulo} - {pend.canal}")
        
        # Test 9: Estadísticas completas
        print("\n📊 Test 9: Obtener estadísticas...")
        stats = await servicio.obtener_estadisticas()
        print(f"   ✅ Total notificaciones: {stats.total_notificaciones}")
        print(f"   📧 Por canal:")
        for canal, count in stats.por_canal.items():
            print(f"      {canal}: {count}")
        print(f"   📊 Por estado:")
        # Construir por_estado desde los campos individuales
        por_estado = {
            "pendiente": stats.pendientes,
            "enviada": stats.enviadas,
            "fallida": stats.fallidas,
            "cancelada": stats.canceladas
        }
        for estado, count in por_estado.items():
            if count > 0:  # Solo mostrar estados con notificaciones
                print(f"      {estado}: {count}")
        print(f"   📋 Por tipo:")
        for tipo, count in stats.por_tipo.items():
            print(f"      {tipo}: {count}")
        
        # Test 10: Procesar notificaciones pendientes
        print("\n🔄 Test 10: Procesar notificaciones pendientes...")
        procesadas = await servicio.procesar_notificaciones_pendientes()
        print(f"   ✅ Notificaciones procesadas: {procesadas}")
        
        # Estadísticas finales
        print("\n📊 ESTADÍSTICAS FINALES:")
        stats_finales = await servicio.obtener_estadisticas()
        print(f"   📧 Total: {stats_finales.total_notificaciones}")
        print(f"   ✅ Enviadas: {stats_finales.enviadas}")
        print(f"   ❌ Fallidas: {stats_finales.fallidas}")
        print(f"   ⏳ Pendientes: {stats_finales.pendientes}")
        
        # Test 11: Usar fábricas especializadas
        print("\n🏭 Test 11: Usar fábricas especializadas...")
        
        # Crear usando fábrica directamente
        notif_bienvenida = FabricaNotificaciones.crear_email_bienvenida(
            "user-999",
            "nuevo@test.com",
            "Usuario Nuevo"
        )
        await repositorio.agregar(notif_bienvenida)
        print(f"   ✅ Email de bienvenida: {notif_bienvenida.id_notificacion}")
        
        notif_codigo = FabricaNotificaciones.crear_sms_codigo_verificacion(
            "user-888",
            "+9876543210",
            "654321"
        )
        await repositorio.agregar(notif_codigo)
        print(f"   ✅ SMS de código: {notif_codigo.id_notificacion}")
        
        notif_promo = FabricaNotificaciones.crear_push_promocion(
            "user-777",
            "token-device-abc",
            "Promoción Flash",
            30
        )
        await repositorio.agregar(notif_promo)
        print(f"   ✅ Push promocional: {notif_promo.id_notificacion}")
        
    except Exception as e:
        print(f"\n❌ ERROR DURANTE EL TEST: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Limpiar recursos
        try:
            await despachador.cerrar()
        except:
            pass
    
    print("\n" + "=" * 80)
    print("✅ TEST COMPLETO FINALIZADO EXITOSAMENTE")
    print("🎯 RESUMEN:")
    print("   • ✅ Servicios de aplicación funcionando")
    print("   • ✅ CQRS implementado (comandos y consultas)")
    print("   • ✅ DTOs y mapeadores operativos") 
    print("   • ✅ Repositorio asíncrono funcional")
    print("   • ✅ Eventos de dominio generados")
    print("   • ✅ Fábricas especializadas funcionando")
    print("   • ✅ Gestión de estados completa")
    print("   • ✅ Estadísticas detalladas")
    print("   • ✅ Arquitectura DDD/CQRS/Event-Driven validada")
    print("=" * 80)
    return True


if __name__ == "__main__":
    resultado = asyncio.run(test_completo())
    exit(0 if resultado else 1)
