"""
Consumer actualizado para escuchar comandos PagoCommand del tópico comando-pago.
Sigue patrón CQRS delegando todo a ejecutar_commando.
"""

import pulsar
import pulsar as _pulsar
from pulsar.schema import AvroSchema
from seedworks.aplicacion.comandos import ejecutar_commando
from ..aplicacion.comandos.pago_command import PagoCommand, PagoData
from config.pulsar_config import PulsarConfig
from schema.comandos_pagos import PagoCommandMessage
import logging
from datetime import datetime

def suscribirse_a_comando_pago():
    """
    Consumer para comandos PagoCommand del tópico comando-pago.
    Según especificación actualizada.
    """
    cliente = None
    try:
        print("🚀 [COMANDO-PAGO CONSUMER] Iniciando...")
        pulsar_config = PulsarConfig()
        cliente = pulsar.Client(pulsar_config.pulsar_url)
        
        consumidor = cliente.subscribe(
            "comando-pago",  # Tópico según especificación
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name='pagos-comando-sub',
            schema=AvroSchema(PagoCommandMessage),
            initial_position=_pulsar.InitialPosition.Earliest
        )

        print("✅ [COMANDO-PAGO CONSUMER] Conectado al tópico 'comando-pago'")

        while True:
            try:
                mensaje = consumidor.receive(timeout_millis=5000)
                
                if mensaje:
                    print(f'📨 [COMANDO-PAGO CONSUMER] PagoCommand recibido')
                    datos = mensaje.value()
                    
                    try:
                        # ✅ Convertir mensaje Avro a comando interno
                        pago_data = PagoData(
                            idEvento=datos.data.idEvento,
                            idSocio=datos.data.idSocio,
                            monto=datos.data.monto,
                            fechaEvento=datetime.fromisoformat(datos.data.fechaEvento.replace('Z', '+00:00'))
                        )
                        
                        comando = PagoCommand(
                            comando=datos.comando,
                            idTransaction=datos.idTransaction,
                            data=pago_data
                        )
                        
                        # 🎯 DELEGACIÓN TOTAL al sistema CQRS!
                        print(f"🔄 [COMANDO-PAGO CONSUMER] Ejecutando comando {datos.comando}")
                        ejecutar_commando(comando)
                        print(f"✅ [COMANDO-PAGO CONSUMER] Comando ejecutado exitosamente")
                        
                    except Exception as e:
                        print(f"❌ [COMANDO-PAGO CONSUMER] Error ejecutando comando: {e}")
                        logging.error(f"Error ejecutando comando: {e}")
                    
                    consumidor.acknowledge(mensaje)
                    
            except pulsar.Timeout:
                continue
            except Exception as e:
                print(f"❌ [COMANDO-PAGO CONSUMER] Error recibiendo mensaje: {e}")
                continue

    except Exception as e:
        logging.error(f'ERROR: [COMANDO-PAGO CONSUMER] Suscribiéndose al tópico comando-pago: {e}')
    finally:
        if cliente:
            cliente.close()

def main_comando_pago_consumer():
    """
    Función principal del consumer de comandos.
    """
    print("🎯 [COMANDO-PAGO CONSUMER] Iniciando consumer para comando-pago")
    suscribirse_a_comando_pago()

if __name__ == "__main__":
    main_comando_pago_consumer()