"""
Consumer refactorizado que sigue EXACTAMENTE el patrón de EventosMS.
Solo maneja infraestructura de mensajería, delega toda la lógica a ejecutar_commando.
"""

import pulsar
import pulsar as _pulsar
from pulsar.schema import AvroSchema
from pagos.seedworks.aplicacion.comandos import ejecutar_commando
from ..aplicacion.comandos.completar_pago import CompletarPagoCommand
from pagos.config.pulsar_config import settings
from pagos.schema.eventos_referidos import ReferidoProcesado  # ✅ Usar schema v2
import logging

def suscribirse_a_eventos_referido_confirmado():
    """
    Consumer refactorizado que SOLO maneja infraestructura.
    Delega toda la lógica de negocio a ejecutar_commando como EventosMS.
    """
    cliente = None
    try:
        print("🚀 [CONSUMER REFACTORIZADO] Iniciando...")
        cliente = pulsar.Client(settings.PULSAR_URL)
        
        consumidor = cliente.subscribe(
            'comando-pago', 
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name='pagos-sub-referidos',
            schema=AvroSchema(ReferidoProcesado),
            initial_position=_pulsar.InitialPosition.Earliest
        )

        print("✅ [CONSUMER REFACTORIZADO] Conectado al tópico 'comando-pago'")

        while True:
            try:
                mensaje = consumidor.receive(timeout_millis=5000)
                
                if mensaje:
                    print(f'📨 [CONSUMER REFACTORIZADO] ReferidoProcesado recibido')  # ✅ Actualizar mensaje
                    datos = mensaje.value()
                    
                    try:
                        # ✅ Crear comando directamente desde los datos del mensaje
                        comando = CompletarPagoCommand(
                            idEvento=datos.idEvento,
                            idSocio=datos.idSocio,
                            monto=datos.monto,
                            fechaEvento=datos.fechaEvento
                        )
                        
                        # 🎯 DELEGACIÓN TOTAL al sistema CQRS!
                        print(f"🔄 [CONSUMER REFACTORIZADO] Ejecutando comando CompletarPago")
                        ejecutar_commando(comando)
                        print(f"✅ [CONSUMER REFACTORIZADO] Comando ejecutado exitosamente")
                        
                    except Exception as e:
                        print(f"❌ [CONSUMER REFACTORIZADO] Error ejecutando comando: {e}")
                        logging.error(f"Error ejecutando comando: {e}")
                    
                    consumidor.acknowledge(mensaje)
                    
            except pulsar.Timeout:
                # Timeout esperando mensaje - continuar el loop
                continue
            except Exception as e:
                print(f"❌ [CONSUMER REFACTORIZADO] Error recibiendo mensaje: {e}")
                continue

    except Exception as e:
        logging.error(f'ERROR: [CONSUMER REFACTORIZADO] Suscribiéndose al tópico referidos: {e}')
    finally:
        if cliente:
            cliente.close()

def main_consumer_refactorizado():
    """
    Función principal del consumer refactorizado.
    Mucho más simple que el worker original.
    """
    print("🎯 [CONSUMER REFACTORIZADO] Iniciando consumer con patrón CQRS")
    suscribirse_a_eventos_referido_confirmado()

if __name__ == "__main__":
    main_consumer_refactorizado()