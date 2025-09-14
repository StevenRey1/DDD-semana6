import pulsar
from pulsar.schema import *
import datetime

# Importamos TODOS los eventos y payloads que este despachador puede manejar
from modulos.referidos.infraestructura.schema.v1.comandos import ComandoConfirmarReferido, ComandoConfirmarReferidoPayload, ComandoCrearReferido, ComandoCrearReferidoPayload
from modulos.referidos.infraestructura.schema.v1.eventos import  EventoReferidoCreado, EventoReferidoConfirmado, EventoReferidoCreadoPayload, EventoReferidoConfirmadoPayload

# Importamos los eventos de tracking (VentaReferidaConfirmada, VentaReferidaRechazada)
from modulos.referidos.infraestructura.schema.v1.eventos_tracking import VentaReferidaConfirmada, VentaReferidaRechazada

# Importamos los eventos de DOMINIO para poder identificarlos
from modulos.referidos.dominio.eventos import ReferidoConfirmado, ReferidoCreado

# Importar configuración de Pulsar
from config.pulsar_config import pulsar_config

from seedwork.infraestructura import utils

epoch = datetime.datetime.utcfromtimestamp(0)

def unix_time_millis(dt):
    print(f"Convirtiendo fecha {dt} a timestamp")
    return (dt - epoch).total_seconds() * 1000.0

class Despachador:
    def _publicar_mensaje(self, mensaje, topico):
        # Usar configuración de Pulsar
        cliente = pulsar.Client(**pulsar_config.client_config)
        # Obtenemos el schema del propio objeto del mensaje
        publicador = cliente.create_producer(topico, schema=AvroSchema(mensaje.__class__), **pulsar_config.producer_config)
        publicador.send(mensaje)
        cliente.close()

    def publicar_evento(self, evento, topico):
        print('===================================================================')
        print(f'¡DESPACHADOR: Publicando evento en el tópico {topico}! evento: {evento}')
        print('===================================================================')
        # =======================================
        # Determinamos el tipo de evento de dominio para saber qué payload crear
        if isinstance(evento, ReferidoCreado):
            payload = EventoReferidoCreadoPayload(
                referido_id=str(evento.idReferido),
                id_afiliado=str(evento.idSocio),
                tipo_accion=str(evento.tipoEvento),
                detalle_accion=f"Monto: {evento.monto}, Estado: {evento.estado}",
                fecha_creacion=int(unix_time_millis(evento.fecha_creacion))
            )
            evento_integracion = EventoReferidoCreado(data=payload)
        elif isinstance(evento, ReferidoConfirmado):
            payload = EventoReferidoConfirmadoPayload(
                referido_id=str(evento.referido_id),
                id_afiliado=str(evento.id_afiliado),
                tipo_accion=str(evento.tipo_accion),
                detalle_accion=str(evento.detalle_accion),
                fecha_actualizacion=int(unix_time_millis(evento.fecha_actualizacion))
            )
            evento_integracion = EventoReferidoConfirmado(data=payload)
        else:
            # Si no reconocemos el evento, no hacemos nada.
            # Podríamos también lanzar un error.
            return

        # Publicamos el evento de integración que acabamos de crear
        self._publicar_mensaje(evento_integracion, topico)

    def publicar_comando(self, comando, topico):
        print('===================================================================')
        print(f'¡DESPACHADOR: Publicando comando en el tópico {topico}! comando: {comando}')
        print('===================================================================')
        # =======================================
        if isinstance(comando, ComandoCrearReferido):
            comando_payload = ComandoCrearReferidoPayload(
                id_referido=str(comando.id_referido),
                id_usuario=str(comando.id_usuario),
                tipo_accion=str(comando.tipo_accion),
                fecha_accion=int(unix_time_millis(comando.fecha_accion)),
                detalle_accion=str(comando.detalle_accion)
            )
            comando = ComandoConfirmarReferido(data=comando_payload)
        elif isinstance(comando, ComandoConfirmarReferido):
            comando_payload = ComandoConfirmarReferidoPayload(
                id_referido=str(comando.id_referido),
                id_usuario=str(comando.id_usuario),
                tipo_accion=str(comando.tipo_accion),
                fecha_accion=int(unix_time_millis(comando.fecha_accion)),
                detalle_accion=str(comando.detalle_accion)
            )
            comando = ComandoConfirmarReferido(data=comando_payload)
        else:
            # Si no reconocemos el comando, no hacemos nada.
            # Podríamos también lanzar un error.
            return
        self._publicar_mensaje(comando, topico)

    def publicar_venta_confirmada(self, datos: dict):
        """
        Publica evento VentaReferidaConfirmada al tópico eventos-referido-confirmado
        
        Args:
            datos: Dict con idReferido, idSocio, monto, fechaConfirmacion
        """
        try:
            print(f"📤 [DESPACHADOR] Publicando VentaReferidaConfirmada: {datos}")
            
            # Generar UUID único para el evento
            import uuid
            evento_id = str(uuid.uuid4())
            
            evento = VentaReferidaConfirmada(
                idEvento=datos['idEvento'],  # UUID único para el evento
                idSocio=datos['idSocio'],
                monto=datos['monto'],  # Usar 'monto' directamente
                fechaEvento=datos['fechaEvento']  # Mapear fechaConfirmacion a fechaEvento
            )
            
            self._publicar_mensaje(evento, 'eventos-referido-confirmado')
            print(f"✅ [DESPACHADOR] VentaReferidaConfirmada publicada exitosamente!")
            
        except Exception as e:
            print(f"❌ [DESPACHADOR] Error publicando VentaReferidaConfirmada: {e}")
            raise e
    
    def publicar_venta_rechazada(self, datos: dict):
        """
        Publica evento VentaReferidaRechazada al tópico eventos-referido-rechazado
        
        Args:
            datos: Dict con idReferido, idSocio, motivo, fechaRechazo
        """
        try:
            print(f"📤 [DESPACHADOR] Publicando VentaReferidaRechazada: {datos}")
            
            # Generar UUID único para el evento
            import uuid
            evento_id = str(uuid.uuid4())
            
            evento = VentaReferidaRechazada(
                idEvento=evento_id  # Solo idEvento según especificación
            )
            
            self._publicar_mensaje(evento, 'eventos-referido-rechazado')
            print(f"✅ [DESPACHADOR] VentaReferidaRechazada publicada exitosamente!")
            
        except Exception as e:
            print(f"❌ [DESPACHADOR] Error publicando VentaReferidaRechazada: {e}")
            raise e