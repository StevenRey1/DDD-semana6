import pulsar
from pulsar.schema import *
import datetime

# Importamos TODOS los eventos y payloads que este despachador puede manejar


# Importamos el nuevo evento unificado
from modulos.referidos.infraestructura.schema.v2.eventos_tracking import ReferidoProcesado



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

    

    def publicar_referido_procesado(self, datos: dict, estado: str):
        """
        Publica un evento ReferidoProcesado al tópico de eventos-referido.
        """
        try:
            print(f"📤 [DESPACHADOR] Publicando ReferidoProcesado con estado '{estado}': {datos}")
            
            evento = ReferidoProcesado(
                idTransaction=datos.get('idTransaction'),
                idEvento=datos.get('idEvento'),
                idSocio=datos.get('idSocio'),
                monto=datos.get('monto'),
                estado_referido=estado,
                fechaEvento=datos.get('fechaEvento')
            )
            
            self._publicar_mensaje(evento, 'eventos-referido')
            print(f"✅ [DESPACHADOR] Evento ReferidoProcesado publicado exitosamente!")
            
        except Exception as e:
            print(f"❌ [DESPACHADOR] Error publicando ReferidoProcesado: {e}")
            raise e
