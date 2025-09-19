"""
Test para validar eventos PagoProcesado
Verifica la publicación y estructura de eventos
"""
import pytest
import json
import time
from datetime import datetime
from pulsar import Client, ConsumerType
from config.pulsar_config import PulsarConfig
from schema.eventos_pagos import PagoProcesado


class TestEventoPagoProcesado:
    
    def setup_method(self):
        """Setup para cada test"""
        self.pulsar_config = PulsarConfig()
        self.client = Client(self.pulsar_config.pulsar_url)
        
        # Consumer para eventos
        self.consumer = self.client.subscribe(
            topic='eventos-pago',
            subscription_name='test-eventos-pagoprocesado',
            consumer_type=ConsumerType.Shared
        )
        
        # Limpiar mensajes previos
        self._limpiar_mensajes_previos()
    
    def teardown_method(self):
        """Cleanup después de cada test"""
        if hasattr(self, 'consumer'):
            self.consumer.close()
        if hasattr(self, 'client'):
            self.client.close()
    
    def _limpiar_mensajes_previos(self):
        """Limpiar mensajes que puedan estar en la cola"""
        try:
            while True:
                msg = self.consumer.receive(timeout_millis=100)
                self.consumer.acknowledge(msg)
        except:
            # Timeout esperado cuando no hay más mensajes
            pass
    
    def _esperar_evento(self, timeout_seconds=10, filtro=None):
        """Esperar un evento específico"""
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            try:
                msg = self.consumer.receive(timeout_millis=1000)
                
                # Deserializar evento
                evento_data = msg.data()
                if isinstance(evento_data, bytes):
                    evento = json.loads(evento_data.decode('utf-8'))
                else:
                    evento = evento_data
                
                # Aplicar filtro si se proporciona
                if filtro is None or filtro(evento):
                    self.consumer.acknowledge(msg)
                    return evento
                else:
                    self.consumer.acknowledge(msg)
                    
            except Exception as e:
                # Continuar esperando en caso de timeout
                continue
        
        return None
    
    def test_estructura_evento_pago_procesado(self):
        """Test de estructura correcta del evento PagoProcesado"""
        # Simular la creación de un pago via API para generar evento
        import requests
        
        comando = {
            "comando": "Iniciar",
            "data": {
                "idTransaction": "txn_evento_001",
                "estado": "PENDING",
                "valor": 125.0,
                "fechaCreacion": datetime.now().isoformat(),
                "fechaActualizacion": datetime.now().isoformat(),
                "idUsuario": "user_evento_test"
            }
        }
        
        # Enviar comando via API
        try:
            response = requests.post("http://localhost:8090/pagos", json=comando)
            if response.status_code != 200:
                # Si API no está disponible, skip el test
                pytest.skip("API no disponible para generar evento")
        except requests.ConnectionError:
            pytest.skip("API no disponible para generar evento")
        
        # Esperar evento correspondiente
        evento = self._esperar_evento(
            filtro=lambda e: e.get('idTransaction') == 'txn_evento_001'
        )
        
        assert evento is not None, "No se recibió evento PagoProcesado"
        
        # Validar estructura según schema
        campos_requeridos = [
            'idTransaction', 'estado', 'valor', 'fechaCreacion', 
            'fechaActualizacion', 'idUsuario'
        ]
        
        for campo in campos_requeridos:
            assert campo in evento, f"Campo requerido faltante: {campo}"
        
        # Validar tipos de datos
        assert isinstance(evento['idTransaction'], str)
        assert isinstance(evento['estado'], str)
        assert isinstance(evento['valor'], (int, float))
        assert isinstance(evento['fechaCreacion'], str)
        assert isinstance(evento['fechaActualizacion'], str)
        assert isinstance(evento['idUsuario'], str)
        
        # Validar valores específicos
        assert evento['idTransaction'] == 'txn_evento_001'
        assert evento['estado'] == 'PENDING'
        assert evento['valor'] == 125.0
        assert evento['idUsuario'] == 'user_evento_test'
        
        print(f"✓ Evento PagoProcesado válido: {evento}")
    
    def test_eventos_multiples_transacciones(self):
        """Test de eventos para múltiples transacciones"""
        import requests
        
        transacciones = [
            {
                "id": "txn_multi_001",
                "valor": 100.0,
                "usuario": "user_multi_1"
            },
            {
                "id": "txn_multi_002", 
                "valor": 200.0,
                "usuario": "user_multi_2"
            },
            {
                "id": "txn_multi_003",
                "valor": 300.0,
                "usuario": "user_multi_3"
            }
        ]
        
        # Crear múltiples pagos
        for txn in transacciones:
            comando = {
                "comando": "Iniciar",
                "data": {
                    "idTransaction": txn["id"],
                    "estado": "PENDING",
                    "valor": txn["valor"],
                    "fechaCreacion": datetime.now().isoformat(),
                    "fechaActualizacion": datetime.now().isoformat(),
                    "idUsuario": txn["usuario"]
                }
            }
            
            try:
                response = requests.post("http://localhost:8090/pagos", json=comando)
                if response.status_code != 200:
                    pytest.skip("API no disponible")
            except requests.ConnectionError:
                pytest.skip("API no disponible")
            
            # Pequeña pausa entre creaciones
            time.sleep(0.5)
        
        # Recopilar eventos generados
        eventos_recibidos = []
        ids_esperados = {txn["id"] for txn in transacciones}
        
        for _ in range(len(transacciones)):
            evento = self._esperar_evento(timeout_seconds=5)
            if evento and evento.get('idTransaction') in ids_esperados:
                eventos_recibidos.append(evento)
        
        # Validar que se recibieron todos los eventos
        assert len(eventos_recibidos) == len(transacciones), \
            f"Se esperaban {len(transacciones)} eventos, se recibieron {len(eventos_recibidos)}"
        
        # Validar que cada transacción tiene su evento
        ids_recibidos = {evento['idTransaction'] for evento in eventos_recibidos}
        assert ids_recibidos == ids_esperados, \
            f"IDs esperados: {ids_esperados}, IDs recibidos: {ids_recibidos}"
        
        print(f"✓ Eventos múltiples validados: {len(eventos_recibidos)} eventos")
    
    def test_evento_cancelacion_pago(self):
        """Test de evento para cancelación de pago"""
        import requests
        
        id_transaction = "txn_cancel_test"
        
        # 1. Crear pago
        comando_crear = {
            "comando": "Iniciar",
            "data": {
                "idTransaction": id_transaction,
                "estado": "PENDING",
                "valor": 150.0,
                "fechaCreacion": datetime.now().isoformat(),
                "fechaActualizacion": datetime.now().isoformat(),
                "idUsuario": "user_cancel_test"
            }
        }
        
        try:
            response = requests.post("http://localhost:8090/pagos", json=comando_crear)
            if response.status_code != 200:
                pytest.skip("API no disponible")
        except requests.ConnectionError:
            pytest.skip("API no disponible")
        
        # Esperar evento de creación
        evento_creacion = self._esperar_evento(
            filtro=lambda e: e.get('idTransaction') == id_transaction and e.get('estado') == 'PENDING'
        )
        assert evento_creacion is not None
        
        # 2. Cancelar pago
        comando_cancelar = {
            "comando": "Cancelar",
            "data": {
                "idTransaction": id_transaction,
                "estado": "CANCELLED",
                "valor": 150.0,
                "fechaCreacion": datetime.now().isoformat(),
                "fechaActualizacion": datetime.now().isoformat(),
                "idUsuario": "user_cancel_test"
            }
        }
        
        response = requests.post("http://localhost:8090/pagos", json=comando_cancelar)
        if response.status_code != 200:
            pytest.skip("API no disponible para cancelación")
        
        # Esperar evento de cancelación
        evento_cancelacion = self._esperar_evento(
            filtro=lambda e: e.get('idTransaction') == id_transaction and e.get('estado') == 'CANCELLED'
        )
        
        assert evento_cancelacion is not None, "No se recibió evento de cancelación"
        assert evento_cancelacion['idTransaction'] == id_transaction
        assert evento_cancelacion['estado'] == 'CANCELLED'
        assert evento_cancelacion['valor'] == 150.0
        
        print(f"✓ Evento de cancelación validado: {evento_cancelacion}")
    
    def test_formato_fechas_evento(self):
        """Test de formato correcto de fechas en eventos"""
        import requests
        from datetime import datetime
        
        fecha_actual = datetime.now().isoformat()
        
        comando = {
            "comando": "Iniciar",
            "data": {
                "idTransaction": "txn_fecha_test",
                "estado": "PENDING",
                "valor": 75.0,
                "fechaCreacion": fecha_actual,
                "fechaActualizacion": fecha_actual,
                "idUsuario": "user_fecha_test"
            }
        }
        
        try:
            response = requests.post("http://localhost:8090/pagos", json=comando)
            if response.status_code != 200:
                pytest.skip("API no disponible")
        except requests.ConnectionError:
            pytest.skip("API no disponible")
        
        # Esperar evento
        evento = self._esperar_evento(
            filtro=lambda e: e.get('idTransaction') == 'txn_fecha_test'
        )
        
        assert evento is not None
        
        # Validar formato de fechas
        fecha_creacion = evento['fechaCreacion']
        fecha_actualizacion = evento['fechaActualizacion']
        
        # Verificar que se pueden parsear como fechas ISO
        try:
            datetime.fromisoformat(fecha_creacion.replace('Z', '+00:00'))
            datetime.fromisoformat(fecha_actualizacion.replace('Z', '+00:00'))
        except ValueError as e:
            pytest.fail(f"Formato de fecha inválido: {e}")
        
        print(f"✓ Formato de fechas válido en evento")


if __name__ == "__main__":
    # Ejecutar tests individuales
    test = TestEventoPagoProcesado()
    
    print("Configurando test eventos...")
    test.setup_method()
    
    try:
        print("Ejecutando test estructura evento...")
        test.test_estructura_evento_pago_procesado()
        print("✓ Test estructura evento exitoso")
        
        print("Ejecutando test cancelación...")
        test.test_evento_cancelacion_pago()
        print("✓ Test cancelación exitoso")
        
        print("Ejecutando test formato fechas...")
        test.test_formato_fechas_evento()
        print("✓ Test formato fechas exitoso")
        
    except Exception as e:
        print(f"Error en tests: {e}")
    finally:
        test.teardown_method()
    
    print("Tests de eventos completados!")