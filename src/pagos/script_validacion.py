#!/usr/bin/env python3
"""
Script de validación completa del servicio de Pagos
Ejecuta todos los tests y validaciones en orden correcto
"""
import sys
import time
import subprocess
import requests
import json
from datetime import datetime
from pathlib import Path


class ValidadorServicioPagos:
    
    def __init__(self):
        self.base_url = "http://localhost:8090"
        self.resultados = []
        self.errores = []
    
    def log(self, mensaje, nivel="INFO"):
        """Log con timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {nivel}: {mensaje}")
    
    def verificar_servicio_disponible(self, max_intentos=30):
        """Verificar que el servicio esté disponible"""
        self.log("Verificando disponibilidad del servicio...")
        
        for intento in range(max_intentos):
            try:
                response = requests.get(f"{self.base_url}/health", timeout=5)
                if response.status_code == 200:
                    self.log("✓ Servicio disponible")
                    return True
            except requests.ConnectionError:
                pass
            
            if intento < max_intentos - 1:
                self.log(f"Esperando servicio... intento {intento + 1}/{max_intentos}")
                time.sleep(2)
        
        self.log("✗ Servicio no disponible", "ERROR")
        return False
    
    def validar_estructura_proyecto(self):
        """Validar que la estructura del proyecto esté correcta"""
        self.log("Validando estructura del proyecto...")
        
        archivos_requeridos = [
            "main.py",
            "modulos/aplicacion/comando_pago_consumer.py",
            "modulos/aplicacion/comandos/pago_command.py",
            "modulos/aplicacion/comandos/pago_command_handler.py",
            "modulos/aplicacion/consultas/obtener_estado_pago.py",
            "schema/comandos_pagos.py",
            "schema/eventos_pagos.py",
            "presentacion/api.py",
            "docker-compose.dev.yml",
            "Dockerfile"
        ]
        
        faltantes = []
        for archivo in archivos_requeridos:
            if not Path(archivo).exists():
                faltantes.append(archivo)
        
        if faltantes:
            self.log(f"✗ Archivos faltantes: {faltantes}", "ERROR")
            self.errores.append(f"Archivos faltantes: {faltantes}")
            return False
        
        self.log("✓ Estructura del proyecto válida")
        return True
    
    def validar_api_health(self):
        """Validar endpoint de health"""
        self.log("Validando endpoint de health...")
        
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                self.log("✓ Health endpoint funcional")
                return True
            else:
                self.log(f"✗ Health endpoint error: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"✗ Error en health endpoint: {e}", "ERROR")
            return False
    
    def validar_api_pagos_iniciar(self):
        """Validar comando Iniciar via API"""
        self.log("Validando comando Iniciar...")
        
        comando = {
            "comando": "Iniciar",
            "data": {
                "idTransaction": f"txn_val_{int(time.time())}",
                "estado": "PENDING",
                "valor": 100.0,
                "fechaCreacion": datetime.now().isoformat(),
                "fechaActualizacion": datetime.now().isoformat(),
                "idUsuario": "user_validation"
            }
        }
        
        try:
            response = requests.post(f"{self.base_url}/pagos", json=comando)
            if response.status_code == 200:
                data = response.json()
                if data.get("idTransaction") == comando["data"]["idTransaction"]:
                    self.log("✓ Comando Iniciar funcional")
                    return True, data
                else:
                    self.log("✗ Respuesta de Iniciar inválida", "ERROR")
                    return False, None
            else:
                self.log(f"✗ Error en comando Iniciar: {response.status_code}", "ERROR")
                return False, None
        except Exception as e:
            self.log(f"✗ Error en comando Iniciar: {e}", "ERROR")
            return False, None
    
    def validar_api_pagos_consultar(self, id_transaction):
        """Validar consulta de estado de pago"""
        self.log("Validando consulta de estado...")
        
        try:
            response = requests.get(f"{self.base_url}/pagos/{id_transaction}")
            if response.status_code == 200:
                data = response.json()
                campos_requeridos = ["idTransaction", "estado", "valor", "fechaCreacion", "fechaActualizacion", "idUsuario"]
                
                for campo in campos_requeridos:
                    if campo not in data:
                        self.log(f"✗ Campo faltante en consulta: {campo}", "ERROR")
                        return False
                
                if data.get("idTransaction") == id_transaction:
                    self.log("✓ Consulta de estado funcional")
                    return True
                else:
                    self.log("✗ ID de transacción no coincide", "ERROR")
                    return False
            else:
                self.log(f"✗ Error en consulta: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"✗ Error en consulta: {e}", "ERROR")
            return False
    
    def validar_api_pagos_cancelar(self, id_transaction):
        """Validar comando Cancelar"""
        self.log("Validando comando Cancelar...")
        
        comando = {
            "comando": "Cancelar",
            "data": {
                "idTransaction": id_transaction,
                "estado": "CANCELLED",
                "valor": 100.0,
                "fechaCreacion": datetime.now().isoformat(),
                "fechaActualizacion": datetime.now().isoformat(),
                "idUsuario": "user_validation"
            }
        }
        
        try:
            response = requests.post(f"{self.base_url}/pagos", json=comando)
            if response.status_code == 200:
                data = response.json()
                if data.get("estado") == "CANCELLED":
                    self.log("✓ Comando Cancelar funcional")
                    return True
                else:
                    self.log("✗ Estado no actualizado a CANCELLED", "ERROR")
                    return False
            else:
                self.log(f"✗ Error en comando Cancelar: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"✗ Error en comando Cancelar: {e}", "ERROR")
            return False
    
    def ejecutar_tests_unitarios(self):
        """Ejecutar suite de tests unitarios"""
        self.log("Ejecutando tests unitarios...")
        
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "test/", "-v"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                self.log("✓ Tests unitarios pasaron")
                return True
            else:
                self.log(f"✗ Tests unitarios fallaron: {result.stderr}", "ERROR")
                return False
        except subprocess.TimeoutExpired:
            self.log("✗ Tests unitarios timeout", "ERROR")
            return False
        except Exception as e:
            self.log(f"✗ Error ejecutando tests: {e}", "ERROR")
            return False
    
    def validar_logs_servicio(self):
        """Validar que no haya errores críticos en logs"""
        self.log("Validando logs del servicio...")
        
        try:
            # Obtener logs del contenedor
            result = subprocess.run(
                ["docker", "logs", "pagos-api"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            logs = result.stdout + result.stderr
            
            # Buscar errores críticos
            errores_criticos = ["ERROR", "CRITICAL", "Exception", "Traceback"]
            errores_encontrados = []
            
            for linea in logs.split('\\n'):
                for error in errores_criticos:
                    if error in linea and "test" not in linea.lower():
                        errores_encontrados.append(linea.strip())
            
            if errores_encontrados:
                self.log(f"⚠️  Errores en logs: {len(errores_encontrados)}", "WARNING")
                for error in errores_encontrados[:5]:  # Mostrar solo los primeros 5
                    self.log(f"  - {error}", "WARNING")
                return False
            else:
                self.log("✓ Logs del servicio limpios")
                return True
                
        except Exception as e:
            self.log(f"⚠️  No se pudieron verificar logs: {e}", "WARNING")
            return True  # No fallo crítico
    
    def generar_reporte(self):
        """Generar reporte final de validación"""
        self.log("=" * 60)
        self.log("REPORTE DE VALIDACIÓN DEL SERVICIO DE PAGOS")
        self.log("=" * 60)
        
        total_validaciones = len(self.resultados)
        exitosas = sum(1 for r in self.resultados if r["resultado"])
        
        self.log(f"Total de validaciones: {total_validaciones}")
        self.log(f"Exitosas: {exitosas}")
        self.log(f"Fallidas: {total_validaciones - exitosas}")
        
        if self.errores:
            self.log("\\nERRORES ENCONTRADOS:")
            for error in self.errores:
                self.log(f"  - {error}", "ERROR")
        
        if exitosas == total_validaciones:
            self.log("\\n🎉 SERVICIO COMPLETAMENTE VALIDADO", "SUCCESS")
            return True
        else:
            self.log("\\n❌ SERVICIO CON PROBLEMAS", "ERROR")
            return False
    
    def ejecutar_validacion_completa(self):
        """Ejecutar validación completa del servicio"""
        self.log("🚀 Iniciando validación completa del servicio de Pagos")
        self.log("=" * 60)
        
        # Lista de validaciones a ejecutar
        validaciones = [
            ("Estructura del proyecto", self.validar_estructura_proyecto),
            ("Servicio disponible", self.verificar_servicio_disponible),
            ("Health endpoint", self.validar_api_health),
            ("Logs del servicio", self.validar_logs_servicio),
        ]
        
        # Ejecutar validaciones básicas
        for nombre, funcion in validaciones:
            try:
                resultado = funcion()
                self.resultados.append({"nombre": nombre, "resultado": resultado})
                if not resultado:
                    self.errores.append(f"Falló: {nombre}")
            except Exception as e:
                self.log(f"✗ Error en {nombre}: {e}", "ERROR")
                self.resultados.append({"nombre": nombre, "resultado": False})
                self.errores.append(f"Error en {nombre}: {e}")
        
        # Si las básicas pasan, hacer validaciones de API
        if all(r["resultado"] for r in self.resultados):
            self.log("\\n--- Validaciones de API ---")
            
            # Test de flujo completo
            resultado_iniciar, data = self.validar_api_pagos_iniciar()
            self.resultados.append({"nombre": "API Iniciar", "resultado": resultado_iniciar})
            
            if resultado_iniciar and data:
                id_transaction = data["idTransaction"]
                
                # Dar tiempo para procesamiento
                time.sleep(2)
                
                resultado_consultar = self.validar_api_pagos_consultar(id_transaction)
                self.resultados.append({"nombre": "API Consultar", "resultado": resultado_consultar})
                
                resultado_cancelar = self.validar_api_pagos_cancelar(id_transaction)
                self.resultados.append({"nombre": "API Cancelar", "resultado": resultado_cancelar})
        
        # Generar reporte final
        return self.generar_reporte()


def main():
    """Función principal"""
    validador = ValidadorServicioPagos()
    
    # Verificar argumentos
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Uso: python script_validacion.py [--skip-tests]")
        print("--skip-tests: Saltar tests unitarios (solo validaciones API)")
        return
    
    skip_tests = "--skip-tests" in sys.argv
    
    try:
        resultado = validador.ejecutar_validacion_completa()
        
        if not skip_tests:
            validador.log("\\n--- Tests Unitarios ---")
            resultado_tests = validador.ejecutar_tests_unitarios()
            validador.resultados.append({"nombre": "Tests Unitarios", "resultado": resultado_tests})
        
        # Resultado final
        resultado_final = validador.generar_reporte()
        sys.exit(0 if resultado_final else 1)
        
    except KeyboardInterrupt:
        validador.log("\\n⚠️  Validación interrumpida por usuario", "WARNING")
        sys.exit(1)
    except Exception as e:
        validador.log(f"\\n💥 Error inesperado: {e}", "ERROR")
        sys.exit(1)


if __name__ == "__main__":
    main()