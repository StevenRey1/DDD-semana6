import pulsar
from pulsar.schema import *

from bff_web import utils

class Despachador:
    def __init__(self):
        ...

    async def publicar_mensaje(self, mensaje, topico, schema):
        try:
            # Intentar consultar el esquema del registry
            json_schema = utils.consultar_schema_registry(schema)
            print(f"✅ Esquema encontrado en registry para {schema}: {json_schema}")
            avro_schema = utils.obtener_schema_avro_de_diccionario(json_schema)
        except Exception as e:
            print(f"⚠️  Esquema no encontrado en registry para {schema}: {e}")
            # Si es el primer mensaje, dejar que Pulsar infiera el esquema
            # eventoMS como consumidor definirá el esquema
            print(f"📝 Publicando primer mensaje en {topico} - eventoMS definirá el esquema")
            avro_schema = None  # Sin esquema para que Pulsar lo infiera

        cliente = pulsar.Client(f'pulsar://{utils.broker_host()}:6650')
        if avro_schema:
            publicador = cliente.create_producer(topico, schema=avro_schema)
        else:
            publicador = cliente.create_producer(topico)  # Sin esquema, Pulsar lo inferirá
        publicador.send(mensaje)
        print(f"✅ Mensaje publicado en {topico}: {mensaje}")
        cliente.close()
