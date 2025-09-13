"""Implementación del repositorio de notificaciones con PostgreSQL"""

import asyncio
import logging
from typing import List, Optional
from datetime import datetime
import asyncpg
import json

from ..dominio.repositorios import RepositorioNotificaciones
from ..dominio.entidades import Notificacion, EstadoNotificacion, TipoNotificacion, CanalNotificacion
from ...config import configuracion

logger = logging.getLogger(__name__)


class RepositorioNotificacionesPostgreSQL(RepositorioNotificaciones):
    """Implementación del repositorio usando PostgreSQL"""
    
    def __init__(self):
        self.pool = None
        self._lock = asyncio.Lock()
    
    async def inicializar(self):
        """Inicializa el pool de conexiones a PostgreSQL"""
        try:
            logger.info(f"🔄 Conectando a PostgreSQL: {configuracion.database_url}")
            
            self.pool = await asyncpg.create_pool(
                configuracion.database_url,
                min_size=1,
                max_size=10,
                command_timeout=60,
                server_settings={
                    'application_name': 'notificaciones_microservice',
                }
            )
            
            # Verificar conexión
            async with self.pool.acquire() as conn:
                result = await conn.fetchval("SELECT version()")
                logger.info(f"🔌 Conectado a PostgreSQL: {result[:50]}...")
            
            await self._crear_tablas()
            logger.info("✅ Repositorio PostgreSQL inicializado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando repositorio PostgreSQL: {e}")
            logger.error(f"📍 URL de conexión: {configuracion.database_url}")
            raise
    
    async def cerrar(self):
        """Cierra el pool de conexiones"""
        if self.pool:
            await self.pool.close()
            logger.info("🔒 Pool de conexiones PostgreSQL cerrado")
    
    async def _crear_tablas(self):
        """Crea las tablas necesarias si no existen"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS notificaciones (
                    id_notificacion VARCHAR(36) PRIMARY KEY,
                    id_usuario VARCHAR(100) NOT NULL,
                    tipo VARCHAR(50) NOT NULL,
                    canal VARCHAR(50) NOT NULL,
                    destinatario VARCHAR(255) NOT NULL,
                    titulo VARCHAR(255) NOT NULL,
                    mensaje TEXT NOT NULL,
                    estado VARCHAR(50) NOT NULL DEFAULT 'pendiente',
                    fecha_creacion TIMESTAMP NOT NULL DEFAULT NOW(),
                    fecha_envio TIMESTAMP NULL,
                    fecha_cancelacion TIMESTAMP NULL,
                    detalle_error TEXT NULL,
                    intentos_envio INTEGER NOT NULL DEFAULT 0,
                    datos_adicionales JSONB NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                );
                
                CREATE INDEX IF NOT EXISTS idx_notificaciones_usuario ON notificaciones(id_usuario);
                CREATE INDEX IF NOT EXISTS idx_notificaciones_estado ON notificaciones(estado);
                CREATE INDEX IF NOT EXISTS idx_notificaciones_fecha_creacion ON notificaciones(fecha_creacion);
            """)
            logger.info("📊 Tablas de notificaciones verificadas/creadas")
    
    def _row_to_notificacion(self, row) -> Notificacion:
        """Convierte una fila de base de datos a entidad Notificacion"""
        return Notificacion(
            id_notificacion=row['id_notificacion'],
            id_usuario=row['id_usuario'],
            tipo=TipoNotificacion(row['tipo']),
            canal=CanalNotificacion(row['canal']),
            destinatario=row['destinatario'],
            titulo=row['titulo'],
            mensaje=row['mensaje'],
            estado=EstadoNotificacion(row['estado']),
            fecha_creacion=row['fecha_creacion'],
            fecha_envio=row['fecha_envio'],
            # fecha_cancelacion se omite porque no existe en la entidad
            detalle_error=row['detalle_error'],
            intentos_envio=row['intentos_envio']
            # datos_adicionales se omite porque no está en la entidad
        )
    
    async def obtener_por_id(self, id_notificacion: str) -> Optional[Notificacion]:
        """Obtiene una notificación por ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM notificaciones WHERE id_notificacion = $1",
                id_notificacion
            )
            if row:
                return self._row_to_notificacion(row)
            return None
    
    async def obtener_por_usuario(self, id_usuario: str, limite: int = None, offset: int = 0) -> List[Notificacion]:
        """Obtiene notificaciones de un usuario con paginación opcional"""
        async with self.pool.acquire() as conn:
            if limite is None:
                rows = await conn.fetch(
                    """SELECT * FROM notificaciones 
                       WHERE id_usuario = $1 
                       ORDER BY fecha_creacion DESC 
                       OFFSET $2""",
                    id_usuario, offset
                )
            else:
                rows = await conn.fetch(
                    """SELECT * FROM notificaciones 
                       WHERE id_usuario = $1 
                       ORDER BY fecha_creacion DESC 
                       LIMIT $2 OFFSET $3""",
                    id_usuario, limite, offset
                )
            
            return [self._row_to_notificacion(row) for row in rows]
    
    async def obtener_por_estado(self, estado: str) -> List[Notificacion]:
        """Obtiene notificaciones por estado"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM notificaciones WHERE estado = $1 ORDER BY fecha_creacion DESC",
                estado
            )
            return [self._row_to_notificacion(row) for row in rows]
    
    async def obtener_pendientes(self) -> List[Notificacion]:
        """Obtiene todas las notificaciones pendientes"""
        return await self.obtener_por_estado("pendiente")
    
    async def agregar(self, notificacion: Notificacion) -> None:
        """Agrega una nueva notificación"""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """INSERT INTO notificaciones (
                    id_notificacion, id_usuario, tipo, canal, destinatario, 
                    titulo, mensaje, estado, fecha_creacion, fecha_envio, 
                    fecha_cancelacion, detalle_error, intentos_envio, datos_adicionales
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)""",
                notificacion.id_notificacion,
                notificacion.id_usuario,
                notificacion.tipo.valor,
                notificacion.canal.valor,
                notificacion.destinatario,
                notificacion.titulo,
                notificacion.mensaje,
                notificacion.estado.valor,
                notificacion.fecha_creacion,
                notificacion.fecha_envio,
                None,  # fecha_cancelacion (no existe en entidad)
                notificacion.detalle_error,
                notificacion.intentos_envio,
                None   # datos_adicionales (no existe en entidad)
            )
            logger.info(f"📝 Notificación agregada a PostgreSQL: {notificacion.id_notificacion}")
    
    async def actualizar(self, notificacion: Notificacion) -> None:
        """Actualiza una notificación existente"""
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                """UPDATE notificaciones SET 
                    id_usuario = $2, tipo = $3, canal = $4, destinatario = $5,
                    titulo = $6, mensaje = $7, estado = $8, fecha_envio = $9,
                    fecha_cancelacion = $10, detalle_error = $11, intentos_envio = $12,
                    datos_adicionales = $13, updated_at = NOW()
                   WHERE id_notificacion = $1""",
                notificacion.id_notificacion,
                notificacion.id_usuario,
                notificacion.tipo.valor,
                notificacion.canal.valor,
                notificacion.destinatario,
                notificacion.titulo,
                notificacion.mensaje,
                notificacion.estado.valor,
                notificacion.fecha_envio,
                None,  # fecha_cancelacion (no existe en entidad)
                notificacion.detalle_error,
                notificacion.intentos_envio,
                None   # datos_adicionales (no existe en entidad)
            )
            
            if result == "UPDATE 0":
                # Si no se actualizó, insertar como nuevo
                await self.agregar(notificacion)
            else:
                logger.info(f"🔄 Notificación actualizada en PostgreSQL: {notificacion.id_notificacion}")
    
    async def eliminar(self, id_notificacion: str) -> None:
        """Elimina una notificación"""
        async with self.pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM notificaciones WHERE id_notificacion = $1",
                id_notificacion
            )
            logger.info(f"🗑️ Notificación eliminada de PostgreSQL: {id_notificacion}")
    
    async def obtener_todas(self, limite: int = 100, offset: int = 0) -> List[Notificacion]:
        """Obtiene todas las notificaciones con paginación"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """SELECT * FROM notificaciones 
                   ORDER BY fecha_creacion DESC 
                   LIMIT $1 OFFSET $2""",
                limite, offset
            )
            logger.info(f"📊 Obteniendo notificaciones de PostgreSQL: {len(rows)} encontradas")
            return [self._row_to_notificacion(row) for row in rows]
    
    async def contar_por_usuario(self, id_usuario: str) -> int:
        """Cuenta las notificaciones de un usuario"""
        async with self.pool.acquire() as conn:
            count = await conn.fetchval(
                "SELECT COUNT(*) FROM notificaciones WHERE id_usuario = $1",
                id_usuario
            )
            return count
    
    async def contar_total(self) -> int:
        """Cuenta el total de notificaciones"""
        async with self.pool.acquire() as conn:
            count = await conn.fetchval("SELECT COUNT(*) FROM notificaciones")
            return count
    
    async def limpiar(self) -> None:
        """Limpia todas las notificaciones (útil para testing)"""
        async with self.pool.acquire() as conn:
            await conn.execute("DELETE FROM notificaciones")
            logger.info("🧹 Todas las notificaciones eliminadas de PostgreSQL")
