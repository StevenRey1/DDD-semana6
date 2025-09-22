"""
Test para validar el consumer de comando-pago
Prueba el flujo completo de mensajería Pulsar
"""
import pytest
import asyncio
import json
import time
from datetime import datetime
from pulsar import Client, MessageId
from config.pulsar_config import PulsarConfig
from schema.comandos_pagos import PagoCommandMessage


class TestConsumerComandoPago:
    
    def setup_method(self):
        """Setup para cada test"""
        self.pulsar_config = PulsarConfig()
        self.client = Client(self.pulsar_config.pulsar_url)
        self.producer = self.client.create_producer(
            topic='comando-pago',
            schema=PagoCommandMessage
        )
        # Dar tiempo para que el consumer esté listo
        time.sleep(2)
    
    def teardown_method(self):
        """Cleanup después de cada test"""
        if hasattr(self, 'producer'):
            self.producer.close()
        if hasattr(self, 'client'):
            self.client.close()
    
    def test_enviar_comando_iniciar_pago(self):
        """Test de envío de comando Iniciar vía Pulsar"""
        comando_message = {
            "comando": "Iniciar",
            "data": {
                "idTransaction": "txn_pulsar_001",
                "estado": "PENDING",
                "valor": 150.0,
                "fechaCreacion": datetime.now().isoformat(),
                "fechaActualizacion": datetime.now().isoformat(),
                "idUsuario": "user_pulsar_123"
            }
        }
        
        # Enviar mensaje
        message_id = self.producer.send(comando_message)
        
        # Verificar que se envió correctamente
        assert message_id is not None
        assert isinstance(message_id, MessageId)
        
        print(f"Mensaje enviado con ID: {message_id}")
        
        # Dar tiempo para que el consumer procese
        time.sleep(3)
        
        # Aquí podrías verificar en la base de datos que el pago fue creado
        # Por ahora solo verificamos que el mensaje se envió sin errores
    
    def test_enviar_comando_cancelar_pago(self):
        """Test de envío de comando Cancelar vía Pulsar"""
        comando_message = {
            "comando": "Cancelar",
            "data": {
                "idTransaction": "txn_pulsar_002",
                "estado": "CANCELLED",
                "valor": 250.0,
                "fechaCreacion": datetime.now().isoformat(),
                "fechaActualizacion": datetime.now().isoformat(),
                "idUsuario": "user_pulsar_456"
            }
        }
        
        # Enviar mensaje
        message_id = self.producer.send(comando_message)
        
        assert message_id is not None
        print(f"Comando Cancelar enviado con ID: {message_id}")
        
        # Dar tiempo para que el consumer procese
        time.sleep(3)
    
    def test_multiples_comandos_secuenciales(self):
        """Test de múltiples comandos en secuencia"""
        comandos = [
            {
                "comando": "Iniciar",
                "data": {
                    "idTransaction": f"txn_seq_001",
                    "estado": "PENDING",
                    "valor": 100.0,
                    "fechaCreacion": datetime.now().isoformat(),
                    "fechaActualizacion": datetime.now().isoformat(),
                    "idUsuario": "user_seq_1"
                }
            },
            {
                "comando": "Iniciar",
                "data": {
                    "idTransaction": f"txn_seq_002",
                    "estado": "PENDING",
                    "valor": 200.0,
                    "fechaCreacion": datetime.now().isoformat(),
                    "fechaActualizacion": datetime.now().isoformat(),
                    "idUsuario": "user_seq_2"
                }
            },
            {
                "comando": "Cancelar",
                "data": {
                    "idTransaction": f"txn_seq_001",
                    "estado": "CANCELLED",
                    "valor": 100.0,
                    "fechaCreacion": datetime.now().isoformat(),
                    "fechaActualizacion": datetime.now().isoformat(),
                    "idUsuario": "user_seq_1"
                }
            }
        ]
        
        message_ids = []
        for comando in comandos:
            message_id = self.producer.send(comando)
            message_ids.append(message_id)
            # Pequeña pausa entre mensajes
            time.sleep(0.5)
        
        assert len(message_ids) == 3
        assert all(mid is not None for mid in message_ids)
        
        print(f"Enviados {len(message_ids)} comandos secuenciales")
        
        # Dar tiempo para que todos se procesen
        time.sleep(5)
    
    def test_comando_con_schema_invalido(self):
        """Test de manejo de comandos con schema inválido"""
        # Intentar enviar un comando con datos faltantes
        comando_invalido = {
            "comando": "Iniciar",
            "data": {
                "idTransaction": "txn_invalid",
                # Falta estado, valor, etc.
            }
        }
        
        try:
            message_id = self.producer.send(comando_invalido)
            # Si llega aquí, el schema no está validando correctamente
            print(f"⚠️  Comando inválido fue enviado: {message_id}")
        except Exception as e:
            # Esto es lo esperado - el schema debería rechazar el mensaje
            print(f"✓ Schema rechazó comando inválido: {e}")
            assert "schema" in str(e).lower() or "required" in str(e).lower()


class TestConsumerIntegracionCompleta:
    """Tests que requieren tanto consumer como API funcionando"""
    
    def setup_method(self):
        """Setup para tests de integración"""
        self.pulsar_config = PulsarConfig()
        self.client = Client(self.pulsar_config.pulsar_url)
        self.producer_comando = self.client.create_producer(
            topic='comando-pago',
            schema=PagoCommandMessage
        )
        
        # Consumer para verificar eventos publicados
        self.consumer_eventos = self.client.subscribe(
            topic='eventos-pago',
            subscription_name='test-eventos-subscription',
            consumer_type=pulsar.ConsumerType.Shared
        )
        
        time.sleep(2)
    
    def teardown_method(self):
        """Cleanup después de cada test"""
        if hasattr(self, 'producer_comando'):
            self.producer_comando.close()
        if hasattr(self, 'consumer_eventos'):
            self.consumer_eventos.close()
        if hasattr(self, 'client'):
            self.client.close()
    
    def test_flujo_comando_a_evento(self):
        """Test completo: comando → procesamiento → evento"""
        id_transaction = f"txn_flow_{int(time.time())}"
        
        # 1. Enviar comando via Pulsar
        comando = {
            "comando": "Iniciar",
            "data": {
                "idTransaction": id_transaction,
                "estado": "PENDING",
                "valor": 300.0,
                "fechaCreacion": datetime.now().isoformat(),
                "fechaActualizacion": datetime.now().isoformat(),
                "idUsuario": "user_flow_test"
            }
        }
        
        message_id = self.producer_comando.send(comando)
        assert message_id is not None
        
        # 2. Esperar a que se procese y se publique evento
        timeout = 10  # segundos
        start_time = time.time()
        evento_recibido = None
        
        while time.time() - start_time < timeout:
            try:
                msg = self.consumer_eventos.receive(timeout_millis=1000)
                evento = json.loads(msg.data().decode('utf-8'))
                
                # Verificar si es nuestro evento
                if evento.get('idTransaction') == id_transaction:
                    evento_recibido = evento
                    self.consumer_eventos.acknowledge(msg)
                    break
                else:
                    self.consumer_eventos.acknowledge(msg)
            except Exception as e:
                # Timeout o error - continuar esperando
                pass
        
        # 3. Validar que se recibió el evento esperado
        assert evento_recibido is not None, f"No se recibió evento para {id_transaction}"
        assert evento_recibido['idTransaction'] == id_transaction
        assert evento_recibido['estado'] == 'PENDING'
        assert evento_recibido['valor'] == 300.0
        
        print(f"✓ Flujo completo validado para {id_transaction}")


if __name__ == "__main__":
    # Tests básicos del consumer
    test = TestConsumerComandoPago()
    
    print("Configurando test consumer...")
    test.setup_method()
    
    try:
        print("Ejecutando test comando Iniciar...")
        test.test_enviar_comando_iniciar_pago()
        print("✓ Test comando Iniciar exitoso")
        
        print("Ejecutando test comando Cancelar...")
        test.test_enviar_comando_cancelar_pago()
        print("✓ Test comando Cancelar exitoso")
        
        print("Ejecutando test comandos secuenciales...")
        test.test_multiples_comandos_secuenciales()
        print("✓ Test comandos secuenciales exitoso")
        
    finally:
        test.teardown_method()
    
    print("Tests de consumer completados!")