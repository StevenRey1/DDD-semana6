"""Consumidores de eventos para el módulo de notificaciones"""

import json
import asyncio
import logging
from typing import Dict, Any
from abc import ABC, abstractmethod

import pulsar

from ...config import configuracion
from ...config.pulsar_config import pulsar_config
from ..aplicacion.servicios import ServicioAplicacionNotificaciones
from ..aplicacion.dto import CrearNotificacionDTO


logger = logging.getLogger(__name__)


class ConsumidorEventosBase(ABC):
    """Clase base para consumidores de eventos"""
    
    def __init__(self, servicio_notificaciones: ServicioAplicacionNotificaciones):
        self.servicio_notificaciones = servicio_notificaciones
        self.cliente_pulsar = None
        self.consumidor = None
        self.running = False
    
    async def inicializar(self):
        """Inicializa la conexión con Pulsar"""
        try:
            self.cliente_pulsar = pulsar.Client(
                pulsar_config.service_url,
                connection_timeout_ms=pulsar_config.consumer_timeout_ms
            )
            
            self.consumidor = self.cliente_pulsar.subscribe(
                self.obtener_topico(),
                subscription_name=self.obtener_suscripcion(),
                consumer_type=pulsar.ConsumerType.Shared
            )
            
            logger.info(f"Consumidor inicializado para tópico: {self.obtener_topico()}")
            
        except Exception as e:
            logger.error(f"Error inicializando consumidor: {e}")
            raise
    
    async def iniciar_consumo(self):
        """Inicia el consumo de eventos"""
        if not self.consumidor:
            await self.inicializar()
        
        self.running = True
        logger.info(f"Iniciando consumo de eventos en {self.obtener_topico()}")
        
        while self.running:
            try:
                # Ejecutar receive() en un hilo separado para no bloquear asyncio
                loop = asyncio.get_event_loop()
                mensaje = await loop.run_in_executor(
                    None, 
                    lambda: self.consumidor.receive(timeout_millis=5000)
                )
                
                if mensaje:
                    await self.procesar_mensaje(mensaje)
                    # Acknowledge también en executor para no bloquear
                    await loop.run_in_executor(
                        None,
                        lambda: self.consumidor.acknowledge(mensaje)
                    )
                    
            except pulsar.Timeout:
                # Timeout normal, continuar
                continue
            except Exception as e:
                logger.error(f"Error procesando mensaje: {e}")
                # En caso de error, seguir consumiendo
                continue
                
            # Ceder control al event loop
            await asyncio.sleep(0.001)
    
    async def detener_consumo(self):
        """Detiene el consumo de eventos"""
        self.running = False
        
        if self.consumidor:
            self.consumidor.close()
        
        if self.cliente_pulsar:
            self.cliente_pulsar.close()
        
        logger.info("Consumo de eventos detenido")
    
    @abstractmethod
    def obtener_topico(self) -> str:
        """Retorna el tópico a consumir"""
        pass
    
    @abstractmethod
    def obtener_suscripcion(self) -> str:
        """Retorna el nombre de la suscripción"""
        pass
    
    @abstractmethod
    async def procesar_mensaje(self, mensaje) -> None:
        """Procesa un mensaje recibido"""
        pass


class ConsumidorEventosPagos(ConsumidorEventosBase):
    """Consumidor de eventos del módulo de pagos"""
    
    def obtener_topico(self) -> str:
        return pulsar_config.get_full_topic_name("eventos-pagos")
    
    def obtener_suscripcion(self) -> str:
        return f"{pulsar_config.subscription_name}-pagos"
    
    async def procesar_mensaje(self, mensaje) -> None:
        """Procesa eventos de pagos para crear notificaciones"""
        try:
            # 🔍 Debug: Ver qué estamos recibiendo
            raw_data = mensaje.data()
            decoded_data = raw_data.decode('utf-8')
            logger.info(f"🔍 Datos RAW recibidos: {repr(raw_data)}")
            logger.info(f"🔍 Datos decodificados: {repr(decoded_data)}")
            
            datos = json.loads(decoded_data)
            estado = datos.get('estado')  # ✅ Cambio: tipo_evento → estado
            
            logger.info(f"🔍 JSON parseado: {datos}")
            logger.info(f"🔍 Estado encontrado: {estado}")
            
            # Según documentación: estados = "solicitado | completado | rechazado"
            if estado == 'completado':  # ✅ Cambio: PagoAprobado → completado
                await self._procesar_pago_completado(datos)
            elif estado == 'rechazado':  # ✅ Cambio: PagoRechazado → rechazado
                await self._procesar_pago_rechazado(datos)
            elif estado == 'solicitado':  # ✅ Cambio: PagoPendiente → solicitado
                await self._procesar_pago_solicitado(datos)
            else:
                logger.warning(f"⚠️ Estado desconocido: {estado}, datos: {datos}")
                
            logger.info(f"Evento de pago procesado: {estado}")
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Error de JSON: {e}")
            logger.error(f"❌ Datos problemáticos: {repr(mensaje.data())}")
            raise
        except Exception as e:
            logger.error(f"Error procesando evento de pago: {e}")
            raise
    
    async def _procesar_pago_completado(self, datos: Dict[str, Any]):  # ✅ Cambio: aprobado → completado
        """Procesa un pago completado creando notificación"""
        logger.info(f"🔄 Procesando pago completado para socio: {datos.get('idSocio')}")  # ✅ Cambio: id_usuario → idSocio
        
        dto = CrearNotificacionDTO(
            id_usuario=datos.get('idSocio'),  # ✅ Cambio: id_usuario → idSocio
            tipo='transaccional',
            canal='email',
            destinatario=f"{datos.get('idSocio')}@alpespartners.com",  # ✅ Cambio: usar idSocio para generar email
            titulo='Pago Completado',  # ✅ Cambio: Aprobado → Completado
            mensaje=f'Tu pago por ${datos.get("monto", 0)} ha sido completado exitosamente.',  # ✅ Cambio: aprobado → completado
            datos_adicionales={
                'idPago': datos.get('idPago'),  # ✅ Cambio: id_pago → idPago
                'idEvento': datos.get('idEvento'),  # ✅ Nuevo campo según documentación
                'monto': datos.get('monto'),
                'fechaPago': datos.get('fechaPago'),  # ✅ Cambio: fecha_creacion → fechaPago
                'estado': datos.get('estado')  # ✅ Nuevo campo según documentación
            }
        )
        
        try:
            result = await self.servicio_notificaciones.crear_notificacion(dto)
            logger.info(f"✅ Notificación creada exitosamente: {result.id_notificacion if result else 'None'}")
        except Exception as e:
            logger.error(f"❌ Error creando notificación: {e}")
            raise
    
    async def _procesar_pago_rechazado(self, datos: Dict[str, Any]):
        """Procesa un pago rechazado creando notificación"""
        dto = CrearNotificacionDTO(
            id_usuario=datos.get('idSocio'),  # ✅ Cambio: id_usuario → idSocio
            tipo='alerta',
            canal='email',
            destinatario=f"{datos.get('idSocio')}@alpespartners.com",  # ✅ Cambio: usar idSocio para generar email
            titulo='Pago Rechazado',
            mensaje=f'Tu pago por ${datos.get("monto", 0)} ha sido rechazado.',  # ✅ Simplificado (no hay motivo en documentación)
            datos_adicionales={
                'idPago': datos.get('idPago'),  # ✅ Cambio: id_pago → idPago
                'idEvento': datos.get('idEvento'),  # ✅ Nuevo campo según documentación
                'monto': datos.get('monto'),
                'fechaPago': datos.get('fechaPago'),  # ✅ Nuevo campo según documentación
                'estado': datos.get('estado')  # ✅ Nuevo campo según documentación
            }
        )
        
        await self.servicio_notificaciones.crear_notificacion(dto)
    
    async def _procesar_pago_solicitado(self, datos: Dict[str, Any]):  # ✅ Cambio: pendiente → solicitado
        """Procesa un pago solicitado creando notificación"""
        dto = CrearNotificacionDTO(
            id_usuario=datos.get('idSocio'),  # ✅ Cambio: id_usuario → idSocio
            tipo='informativa',
            canal='email',
            destinatario=f"{datos.get('idSocio')}@alpespartners.com",  # ✅ Cambio: usar idSocio para generar email
            titulo='Pago Solicitado',  # ✅ Cambio: en Proceso → Solicitado
            mensaje=f'Tu pago por ${datos.get("monto", 0)} ha sido solicitado. Te notificaremos cuando esté completo.',  # ✅ Cambio: procesado → solicitado
            datos_adicionales={
                'idPago': datos.get('idPago'),  # ✅ Cambio: id_pago → idPago
                'idEvento': datos.get('idEvento'),  # ✅ Nuevo campo según documentación
                'monto': datos.get('monto'),
                'fechaPago': datos.get('fechaPago'),  # ✅ Nuevo campo según documentación
                'estado': datos.get('estado')  # ✅ Nuevo campo según documentación
            }
        )
        
        await self.servicio_notificaciones.crear_notificacion(dto)


class ConsumidorEventosReferidos(ConsumidorEventosBase):
    """Consumidor de eventos del módulo de referidos"""
    
    def obtener_topico(self) -> str:
        return pulsar_config.get_full_topic_name("eventos-referidos")
    
    def obtener_suscripcion(self) -> str:
        return f"{pulsar_config.subscription_name}-referidos"
    
    async def procesar_mensaje(self, mensaje) -> None:
        """Procesa eventos de referidos para crear notificaciones"""
        try:
            datos = json.loads(mensaje.data().decode('utf-8'))
            tipo_evento = datos.get('tipo_evento')
            
            if tipo_evento == 'ReferidoCreado':
                await self._procesar_referido_creado(datos)
            elif tipo_evento == 'ReferidoActivado':
                await self._procesar_referido_activado(datos)
                
            logger.info(f"Evento de referido procesado: {tipo_evento}")
            
        except Exception as e:
            logger.error(f"Error procesando evento de referido: {e}")
            raise
    
    async def _procesar_referido_creado(self, datos: Dict[str, Any]):
        """Procesa un referido creado"""
        # Notificar al referidor
        dto_referidor = CrearNotificacionDTO(
            id_usuario=datos.get('id_referidor'),
            tipo='informativa',
            canal='email',
            destinatario=datos.get('email_referidor'),
            titulo='Nuevo Referido',
            mensaje=f'¡Felicidades! Has referido a {datos.get("nombre_referido")}. Cuando se active obtendrás tus beneficios.',
            datos_adicionales={
                'id_referido': datos.get('id_referido'),
                'nombre_referido': datos.get('nombre_referido')
            }
        )
        
        await self.servicio_notificaciones.crear_notificacion(dto_referidor)
        
        # Notificar al referido
        dto_referido = CrearNotificacionDTO(
            id_usuario=datos.get('id_referido'),
            tipo='bienvenida',
            canal='email',
            destinatario=datos.get('email_referido'),
            titulo='¡Bienvenido!',
            mensaje=f'¡Bienvenido! Has sido referido por {datos.get("nombre_referidor")}. Completa tu registro para activar los beneficios.',
            datos_adicionales={
                'id_referidor': datos.get('id_referidor'),
                'nombre_referidor': datos.get('nombre_referidor')
            }
        )
        
        await self.servicio_notificaciones.crear_notificacion(dto_referido)
    
    async def _procesar_referido_activado(self, datos: Dict[str, Any]):
        """Procesa un referido activado"""
        dto = CrearNotificacionDTO(
            id_usuario=datos.get('id_referidor'),
            tipo='recompensa',
            canal='email',
            destinatario=datos.get('email_referidor'),
            titulo='¡Referido Activado!',
            mensaje=f'Tu referido {datos.get("nombre_referido")} se ha activado. ¡Has ganado ${datos.get("recompensa", 0)} en créditos!',
            datos_adicionales={
                'id_referido': datos.get('id_referido'),
                'nombre_referido': datos.get('nombre_referido'),
                'recompensa': datos.get('recompensa')
            }
        )
        
        await self.servicio_notificaciones.crear_notificacion(dto)


class ConsumidorEventosSistema(ConsumidorEventosBase):
    """Consumidor de eventos del sistema (registro_eventos)"""
    
    def obtener_topico(self) -> str:
        return pulsar_config.get_full_topic_name("eventos-sistema")
    
    def obtener_suscripcion(self) -> str:
        return f"{pulsar_config.subscription_name}-sistema"
    
    async def procesar_mensaje(self, mensaje) -> None:
        """Procesa eventos del sistema para crear notificaciones"""
        try:
            datos = json.loads(mensaje.data().decode('utf-8'))
            tipo_evento = datos.get('tipoEvento')
            
            logger.info(f"🔄 Procesando evento del sistema: {tipo_evento}")
            
            # Procesar según el tipo de evento
            if tipo_evento in ['PagoAprobado', 'PagoRechazado', 'PagoPendiente']:
                await self._procesar_evento_pago_sistema(datos)
            elif tipo_evento in ['ReferidoCreado', 'ReferidoActivado']:
                await self._procesar_evento_referido_sistema(datos)
            else:
                # Evento genérico del sistema
                await self._procesar_evento_generico(datos)
                
        except Exception as e:
            logger.error(f"Error procesando evento del sistema: {e}")
            raise
    
    async def _procesar_evento_pago_sistema(self, datos: Dict[str, Any]):
        """Procesa eventos de pago que llegan desde el sistema"""
        evento_data = datos.get('evento', {})
        
        dto = CrearNotificacionDTO(
            id_usuario=evento_data.get('idSocio', 'admin'),  # ✅ Cambio: id_usuario → idSocio
            tipo='sistema',
            canal='email',  # 🔥 CAMBIADO: de 'sistema' a 'email'
            destinatario='admin@sistema.com',
            titulo=f'Evento de Sistema: {datos.get("tipoEvento")}',
            mensaje=f'Se registró un evento de pago en el sistema: {datos.get("tipoEvento")}',
            datos_adicionales={
                'evento_id': datos.get('id'),
                'tipo_evento': datos.get('tipoEvento'),
                'fecha_registro': datos.get('fechaRegistro'),
                'evento_completo': evento_data
            }
        )
        
        await self.servicio_notificaciones.crear_notificacion(dto)
    
    async def _procesar_evento_referido_sistema(self, datos: Dict[str, Any]):
        """Procesa eventos de referido que llegan desde el sistema"""
        evento_data = datos.get('evento', {})
        
        dto = CrearNotificacionDTO(
            id_usuario=evento_data.get('idSocio', 'admin'),  # ✅ Cambio: id_usuario → idSocio
            tipo='sistema',
            canal='email',  # 🔥 CAMBIADO: de 'sistema' a 'email'
            destinatario='admin@sistema.com',
            titulo=f'Evento de Sistema: {datos.get("tipoEvento")}',
            mensaje=f'Se registró un evento de referido en el sistema: {datos.get("tipoEvento")}',
            datos_adicionales={
                'evento_id': datos.get('id'),
                'tipo_evento': datos.get('tipoEvento'),
                'fecha_registro': datos.get('fechaRegistro'),
                'evento_completo': evento_data
            }
        )
        
        await self.servicio_notificaciones.crear_notificacion(dto)
    
    async def _procesar_evento_generico(self, datos: Dict[str, Any]):
        """Procesa cualquier otro evento del sistema"""
        dto = CrearNotificacionDTO(
            id_usuario='admin',
            tipo='sistema',
            canal='email',  # 🔥 CAMBIADO: de 'sistema' a 'email'
            destinatario='admin@sistema.com',
            titulo=f'Evento del Sistema: {datos.get("tipoEvento", "Desconocido")}',
            mensaje=f'Se registró un evento en el sistema de tipo: {datos.get("tipoEvento", "Desconocido")}',
            datos_adicionales={
                'evento_id': datos.get('id'),
                'tipo_evento': datos.get('tipoEvento'),
                'fecha_registro': datos.get('fechaRegistro'),
                'evento_completo': datos.get('evento', {})
            }
        )
        
        await self.servicio_notificaciones.crear_notificacion(dto)


class ConsumidorEventosReferidosRechazados(ConsumidorEventosBase):
    """Consumidor específico para eventos de referidos rechazados"""
    
    def obtener_topico(self) -> str:
        return pulsar_config.get_full_topic_name("eventos-referidos-rechazado")
    
    def obtener_suscripcion(self) -> str:
        return f"{pulsar_config.subscription_name}-referidos-rechazados"
    
    async def procesar_mensaje(self, mensaje) -> None:
        """Procesa eventos de referidos rechazados para crear notificaciones"""
        try:
            datos = json.loads(mensaje.data().decode('utf-8'))
            
            # Según la documentación, el evento es VentaReferidaRechazada
            # Estructura: { "idEvento": "uuid" }
            await self._procesar_referido_rechazado(datos)
                
            logger.info(f"Evento de referido rechazado procesado: {datos.get('idEvento')}")
            
        except Exception as e:
            logger.error(f"Error procesando evento de referido rechazado: {e}")
            raise
    
    async def _procesar_referido_rechazado(self, datos: Dict[str, Any]):
        """Procesa un referido rechazado creando notificaciones"""
        logger.info(f"🔄 Procesando referido rechazado para evento: {datos.get('idEvento')}")
        
        # Según la documentación solo tenemos el idEvento
        # Necesitaremos obtener más información del evento o trabajar con lo disponible
        dto = CrearNotificacionDTO(
            id_usuario=datos.get('idSocio', 'admin'),  # Si no viene idSocio, usar admin
            tipo='alerta',
            canal='email',
            destinatario=datos.get('email', 'admin@alpespartners.com'),  # Email por defecto
            titulo='Referido Rechazado',
            mensaje=f'El referido asociado al evento {datos.get("idEvento")} ha sido rechazado. Por favor revisa los detalles.',
            datos_adicionales={
                'id_evento': datos.get('idEvento'),
                'fecha_rechazo': datos.get('fechaRechazo'),
                'motivo': datos.get('motivo', 'No especificado')
            }
        )
        
        try:
            result = await self.servicio_notificaciones.crear_notificacion(dto)
            logger.info(f"✅ Notificación de referido rechazado creada: {result.id_notificacion if result else 'None'}")
        except Exception as e:
            logger.error(f"❌ Error creando notificación de referido rechazado: {e}")
            raise


class OrquestadorConsumidores:
    """Orquestador que maneja múltiples consumidores"""
    
    def __init__(self, servicio_notificaciones: ServicioAplicacionNotificaciones):
        self.servicio_notificaciones = servicio_notificaciones
        self.consumidores = [
            ConsumidorEventosPagos(servicio_notificaciones),
            ConsumidorEventosReferidos(servicio_notificaciones),
            ConsumidorEventosReferidosRechazados(servicio_notificaciones),  # 🔥 NUEVO
            ConsumidorEventosSistema(servicio_notificaciones)
        ]
        self.tareas = []
    
    async def iniciar_todos(self):
        """Inicia todos los consumidores"""
        logger.info("Iniciando todos los consumidores de eventos")
        
        for consumidor in self.consumidores:
            # Crear tareas de background usando asyncio.create_task()
            tarea = asyncio.create_task(consumidor.iniciar_consumo())
            self.tareas.append(tarea)
        
        logger.info(f"Iniciados {len(self.consumidores)} consumidores")
        
        # No hacer await de las tareas para que corran en background
    
    async def detener_todos(self):
        """Detiene todos los consumidores"""
        logger.info("Deteniendo todos los consumidores")
        
        # Detener consumidores
        for consumidor in self.consumidores:
            await consumidor.detener_consumo()
        
        # Cancelar tareas
        for tarea in self.tareas:
            tarea.cancel()
        
        # Esperar a que terminen
        await asyncio.gather(*self.tareas, return_exceptions=True)
        
        logger.info("Todos los consumidores detenidos")
