import pulsar
from pulsar.schema import AvroSchema
from modulos.referidos.infraestructura.schema.v2.eventos_tracking import EventoRegistrado, EventoRegistradoPayload
from config.pulsar_config import pulsar_config

def send_test_event():
    client = pulsar.Client(**pulsar_config.client_config)
    producer = client.create_producer(
        'comando-referido',
        schema=AvroSchema(EventoRegistrado)
    )

    payload = EventoRegistradoPayload(
        idEvento="4b967ffb-4a80-4843-a59a-dc555b45493f",
        tipoEvento="venta_creada",
        idReferido="0159c84a-429f-40d7-94c8-e3c5a27c2d5d",
        idSocio="835c8d61-d47a-4a89-a1dd-e098c903866b", 
        monto=1111.50,
        estado="pendiente",   
        fechaEvento="2025-09-09T20:00:00Z"
    )
    evento = EventoRegistrado(
        idTransaction = "5b967ffb-4a80-4843-a59a-dc555b45493f",
        data=payload
    )
    # Si tu esquema EventoRegistrado tiene idTransaction, agrégalo así:
    # evento.idTransaction = "5b967ffb-4a80-4843-a59a-dc555b45493f"
    producer.send(evento)
    print("Mensaje enviado a comando-referido")
    client.close()

if __name__ == "__main__":
    send_test_event()