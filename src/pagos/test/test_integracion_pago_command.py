"""
DEPRECADO: Test de integración antiguo basado en un contrato previo (snake_case y campos diferentes).
Se mantiene el archivo como referencia histórica pero NO debe ejecutarse en la suite actual.
Marcado con skip global de pytest.
"""
import pytest
pytestmark = pytest.mark.skip(reason="Contrato antiguo de PagoCommand; usar test_microservicio_completo.py actualizado")
import requests
import time
import json
from datetime import datetime
from config.pulsar_config import PulsarConfig


class TestIntegracionPagoCommand:
    
    BASE_URL = "http://localhost:8090"
    
    @classmethod
    def setup_class(cls):
        """Setup que espera a que el servicio esté disponible"""
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{cls.BASE_URL}/health")
                if response.status_code == 200:
                    print("Servicio disponible")
                    return
            except requests.ConnectionError:
                pass
            time.sleep(2)
        raise Exception("Servicio no disponible después de esperar")
    
    def test_comando_iniciar_pago_exitoso(self):
        """Test completo de inicio de pago"""
        comando = {
            "comando": "Iniciar",
            "data": {
                "idTransaction": "txn_001_test",
                "estado": "PENDING",
                "valor": 100.00,
                "fechaCreacion": datetime.now().isoformat(),
                "fechaActualizacion": datetime.now().isoformat(),
                "idUsuario": "user_123"
            }
        }
        
        response = requests.post(f"{self.BASE_URL}/pagos", json=comando)
        
        assert response.status_code == 200
        data = response.json()
        
        # Validar estructura de respuesta según contrato
        assert "idTransaction" in data
        assert "estado" in data
        assert "fechaCreacion" in data
        assert data["idTransaction"] == "txn_001_test"
        assert data["estado"] == "PENDING"
    
    def test_comando_cancelar_pago_exitoso(self):
        """Test completo de cancelación de pago"""
        # Primero crear un pago
        comando_iniciar = {
            "comando": "Iniciar",
            "data": {
                "idTransaction": "txn_002_test",
                "estado": "PENDING",
                "valor": 200.00,
                "fechaCreacion": datetime.now().isoformat(),
                "fechaActualizacion": datetime.now().isoformat(),
                "idUsuario": "user_456"
            }
        }
        
        response_iniciar = requests.post(f"{self.BASE_URL}/pagos", json=comando_iniciar)
        assert response_iniciar.status_code == 200
        
        # Ahora cancelar
        comando_cancelar = {
            "comando": "Cancelar",
            "data": {
                "idTransaction": "txn_002_test",
                "estado": "CANCELLED",
                "valor": 200.00,
                "fechaCreacion": datetime.now().isoformat(),
                "fechaActualizacion": datetime.now().isoformat(),
                "idUsuario": "user_456"
            }
        }
        
        response = requests.post(f"{self.BASE_URL}/pagos", json=comando_cancelar)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["idTransaction"] == "txn_002_test"
        assert data["estado"] == "CANCELLED"
    
    def test_consultar_estado_pago(self):
        """Test de consulta de estado usando ObtenerEstadoPagoQuery"""
        # Crear un pago primero
        comando = {
            "comando": "Iniciar",
            "data": {
                "idTransaction": "txn_003_test",
                "estado": "PENDING",
                "valor": 300.00,
                "fechaCreacion": datetime.now().isoformat(),
                "fechaActualizacion": datetime.now().isoformat(),
                "idUsuario": "user_789"
            }
        }
        
        response_crear = requests.post(f"{self.BASE_URL}/pagos", json=comando)
        assert response_crear.status_code == 200
        
        # Dar tiempo para que se procese
        time.sleep(1)
        
        # Consultar estado
        response = requests.get(f"{self.BASE_URL}/pagos/txn_003_test")
        
        assert response.status_code == 200
        data = response.json()
        
        # Validar estructura según especificación
        assert "idTransaction" in data
        assert "estado" in data
        assert "valor" in data
        assert "fechaCreacion" in data
        assert "fechaActualizacion" in data
        assert "idUsuario" in data
        
        assert data["idTransaction"] == "txn_003_test"
        assert data["estado"] == "PENDING"
        assert data["valor"] == 300.00
        assert data["idUsuario"] == "user_789"
    
    def test_pago_no_encontrado(self):
        """Test de pago no encontrado"""
        response = requests.get(f"{self.BASE_URL}/pagos/txn_inexistente")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_comando_invalido(self):
        """Test de comando inválido"""
        comando_invalido = {
            "comando": "ComandoInvalido",
            "data": {
                "idTransaction": "txn_004_test",
                "estado": "PENDING"
            }
        }
        
        response = requests.post(f"{self.BASE_URL}/pagos", json=comando_invalido)
        
        # Debería fallar por comando inválido
        assert response.status_code in [400, 422]
    
    def test_validacion_campos_requeridos(self):
        """Test de validación de campos requeridos"""
        comando_incompleto = {
            "comando": "Iniciar",
            "data": {
                "estado": "PENDING"
                # Falta idTransaction y otros campos requeridos
            }
        }
        
        response = requests.post(f"{self.BASE_URL}/pagos", json=comando_incompleto)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_flujo_completo_pago(self):
        """Test de flujo completo: crear, consultar, cancelar"""
        id_transaction = f"txn_flow_{int(time.time())}"
        
        # 1. Crear pago
        comando_crear = {
            "comando": "Iniciar",
            "data": {
                "idTransaction": id_transaction,
                "estado": "PENDING",
                "valor": 500.00,
                "fechaCreacion": datetime.now().isoformat(),
                "fechaActualizacion": datetime.now().isoformat(),
                "idUsuario": "user_flow_test"
            }
        }
        
        response_crear = requests.post(f"{self.BASE_URL}/pagos", json=comando_crear)
        assert response_crear.status_code == 200
        
        # 2. Consultar estado
        time.sleep(1)
        response_consultar = requests.get(f"{self.BASE_URL}/pagos/{id_transaction}")
        assert response_consultar.status_code == 200
        data_consultar = response_consultar.json()
        assert data_consultar["estado"] == "PENDING"
        
        # 3. Cancelar pago
        comando_cancelar = {
            "comando": "Cancelar",
            "data": {
                "idTransaction": id_transaction,
                "estado": "CANCELLED",
                "valor": 500.00,
                "fechaCreacion": datetime.now().isoformat(),
                "fechaActualizacion": datetime.now().isoformat(),
                "idUsuario": "user_flow_test"
            }
        }
        
        response_cancelar = requests.post(f"{self.BASE_URL}/pagos", json=comando_cancelar)
        assert response_cancelar.status_code == 200
        
        # 4. Verificar estado final
        time.sleep(1)
        response_final = requests.get(f"{self.BASE_URL}/pagos/{id_transaction}")
        assert response_final.status_code == 200
        data_final = response_final.json()
        assert data_final["estado"] == "CANCELLED"


if __name__ == "__main__":
    # Ejecutar tests individuales para debugging
    test = TestIntegracionPagoCommand()
    test.setup_class()
    
    print("Ejecutando test de comando iniciar...")
    test.test_comando_iniciar_pago_exitoso()
    print("✓ Test comando iniciar exitoso")
    
    print("Ejecutando test de consulta estado...")
    test.test_consultar_estado_pago()
    print("✓ Test consulta estado exitoso")
    
    print("Ejecutando test de flujo completo...")
    test.test_flujo_completo_pago()
    print("✓ Test flujo completo exitoso")
    
    print("Todos los tests completados exitosamente!")