import pulsar
from pulsar.schema import *
import datetime

from modulos.referidos.infraestructura.schema.v1.eventos import VentaReferidaConfirmada, VentaReferidaConfirmadaPayload, VentaReferidaRechazada, VentaReferidaRechazadaPayload
from modulos.referidos.dominio.eventos import VentaReferidaConfirmada as DominioVentaReferidaConfirmada, VentaReferidaRechazada as DominioVentaReferidaRechazada
from seedwork.infraestructura import utils

epoch = datetime.datetime.utcfromtimestamp(0)

def unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0

class Despachador:
    def _publicar_mensaje(self, mensaje, topico):
        cliente = pulsar.Client(f'pulsar://{utils.broker_host()}:6650')
        publicador = cliente.create_producer(topico, schema=AvroSchema(mensaje.__class__))
        publicador.send(mensaje)
        cliente.close()

    def publicar_evento(self, evento, topico):
        print('===================================================================')
        print(f'¡DESPACHADOR: Publicando evento en el tópico {topico}! evento: {evento}')
        print('===================================================================')
        
        if isinstance(evento, DominioVentaReferidaConfirmada):
            payload = VentaReferidaConfirmadaPayload(
                id_evento=str(evento.id_evento),
                id_socio=str(evento.id_socio),
                monto=evento.monto,
                fecha_evento=str(evento.fecha_evento)
            )
            evento_integracion = VentaReferidaConfirmada(data=payload)
            self._publicar_mensaje(evento_integracion, topico)
        elif isinstance(evento, DominioVentaReferidaRechazada):
            payload = VentaReferidaRechazadaPayload(
                id_evento=str(evento.id_evento)
            )
            evento_integracion = VentaReferidaRechazada(data=payload)
            self._publicar_mensaje(evento_integracion, topico)
        else:
            return

    def publicar_comando(self, comando, topico):
        # No hay comandos definidos para publicar en este microservicio
        pass
