import pulsar
import os
import sys
from pathlib import Path

# Add the project root to the sys.path to allow importing project modules
project_root = Path(__file__).resolve().parents[4] # Adjust this path if necessary
sys.path.append(str(project_root))

# Import PulsarConfig from the referidos module
from config.pulsar_config import pulsar_config
from modulos.referidos.infraestructura.schema.v1.eventos_tracking import ReferidoProcesado

def consume_referido_events():
    client = None
    consumer = None
    try:
        # Initialize Pulsar client using the project's configuration
        client = pulsar.Client(**pulsar_config.client_config)

        # Define the topic and subscription name
        topic = 'eventos-referido'
        subscription_name = 'referidos-event-subscriber'

        # Create a consumer
        consumer = client.subscribe(
            topic,
            subscription_name,
            consumer_type=pulsar.ConsumerType.Shared,
            schema=pulsar.schema.AvroSchema(ReferidoProcesado)
        )

        print(f"[*] Listening for messages on topic '{topic}'...")
        print("Press Ctrl+C to exit.")

        while True:
            msg = consumer.receive()
            try:
                # *** CHANGE THIS LINE ***
                print(f"Received message: {msg.value()}")
                consumer.acknowledge(msg)
            except Exception as e:
                print(f"Error processing message: {e}")
                consumer.negative_acknowledge(msg)

    except KeyboardInterrupt:
        print("\n[*] Consumer stopped by user.")
    except Exception as e:
        print(f"[!] An error occurred: {e}")
    finally:
        if consumer:
            consumer.close()
        if client:
            client.close()

if __name__ == "__main__":
    consume_referido_events()