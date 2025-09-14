"""
Test simple del microservicio de notificaciones
"""

import asyncio
import sys
import os

# Agregar el directorio actual al path para importaciones
sys.path.insert(0, os.path.dirname(__file__))

async def test_basico():
    """Test básico de funcionalidad"""
    print("🧪 Iniciando test básico del microservicio de notificaciones")
    print("=" * 60)
    
    try:
        # Test 1: Importar entidades
        print("📦 Test 1: Importando entidades...")
        from modulos.dominio.entidades import Notificacion
        from modulos.dominio.objetos_valor import TipoNotificacion, CanalNotificacion, EstadoNotificacion
        from modulos.dominio.fabricas import FabricaNotificaciones
        print("   ✅ Entidades importadas correctamente")
        
        # Test 2: Crear notificación usando fábrica
        print("\n🏭 Test 2: Creando notificación con fábrica...")
        notificacion = FabricaNotificaciones.crear_email_bienvenida(
            "user-123",
            "usuario@test.com", 
            "Usuario Test"
        )
        print(f"   ✅ Notificación creada: {notificacion.id_notificacion}")
        print(f"   📧 Tipo: {notificacion.tipo.valor}")
        print(f"   📨 Canal: {notificacion.canal.valor}")
        print(f"   📊 Estado: {notificacion.estado.valor}")
        
        # Test 3: Verificar eventos
        print("\n📡 Test 3: Verificando eventos de dominio...")
        print(f"   📊 Eventos generados: {len(notificacion.eventos)}")
        if notificacion.eventos:
            evento = notificacion.eventos[0]
            print(f"   🎯 Primer evento: {evento.__class__.__name__}")
        
        # Test 4: Repositorio en memoria
        print("\n💾 Test 4: Probando repositorio en memoria...")
        from modulos.infraestructura.repositorios import RepositorioNotificacionesMemoria
        
        repo = RepositorioNotificacionesMemoria()
        await repo.agregar(notificacion)
        
        # Buscar por ID
        encontrada = await repo.obtener_por_id(notificacion.id_notificacion)
        if encontrada:
            print(f"   ✅ Notificación encontrada por ID: {encontrada.id_notificacion}")
        else:
            print("   ❌ No se pudo encontrar la notificación")
        
        # Buscar por usuario
        por_usuario = await repo.obtener_por_usuario("user-123")
        print(f"   📊 Notificaciones del usuario: {len(por_usuario)}")
        
        # Test 5: DTOs y mapeadores
        print("\n📋 Test 5: Probando DTOs y mapeadores...")
        from modulos.aplicacion.mapeadores import MapeadorNotificacion
        from modulos.aplicacion.dto import CrearNotificacionDTO
        
        mapeador = MapeadorNotificacion()
        dto = mapeador.entidad_a_dto(notificacion)
        print(f"   ✅ DTO creado: {dto.id_notificacion}")
        print(f"   📧 Mensaje: {dto.mensaje[:50]}...")
        
        # Test 6: Crear otra notificación diferente
        print("\n📱 Test 6: Creando notificación SMS...")
        sms_notif = FabricaNotificaciones.crear_sms_codigo_verificacion(
            "user-456",
            "+1234567890",
            "123456"
        )
        await repo.agregar(sms_notif)
        print(f"   ✅ SMS creado: {sms_notif.id_notificacion}")
        print(f"   📱 Destinatario: {sms_notif.destinatario}")
        
        # Test 7: Estadísticas básicas
        print("\n📊 Test 7: Estadísticas básicas...")
        total = await repo.contar_total()
        pendientes = await repo.obtener_pendientes()
        print(f"   📊 Total notificaciones: {total}")
        print(f"   ⏳ Pendientes: {len(pendientes)}")
        
        # Test 8: Enviar notificación (cambiar estado)
        print("\n📤 Test 8: Simulando envío...")
        notificacion.marcar_como_enviada()
        await repo.actualizar(notificacion)
        
        actualizada = await repo.obtener_por_id(notificacion.id_notificacion)
        if actualizada:
            print(f"   ✅ Estado actualizado: {actualizada.estado.valor}")
            print(f"   ⏰ Fecha envío: {actualizada.fecha_envio}")
        
        print(f"\n📊 Resumen final:")
        print(f"   📧 Total notificaciones en repo: {await repo.contar_total()}")
        print(f"   ⏳ Pendientes: {len(await repo.obtener_pendientes())}")
        
        todas = await repo.obtener_todas()
        for notif in todas:
            print(f"   📝 {notif.id_notificacion[:8]}... - {notif.tipo.valor} - {notif.estado.valor}")
        
    except Exception as e:
        print(f"\n❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("✅ Test básico completado exitosamente")
    return True


if __name__ == "__main__":
    resultado = asyncio.run(test_basico())
    exit(0 if resultado else 1)
