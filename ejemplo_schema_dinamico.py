"""
Ejemplo de cómo crear schemas dinámicamente al leer mensajes
"""

import json
import pulsar
from pulsar.schema import AvroSchema

class ConsumidorSchemaDinamico:
    """Consumidor que crea schemas dinámicamente"""
    
    def __init__(self):
        self.schemas_cache = {}
    
    def crear_consumer_sin_schema(self, topico):
        """Crea consumidor sin schema específico"""
        cliente = pulsar.Client('pulsar://localhost:6650')
        
        # ❌ Sin schema - recibe datos binarios
        consumidor = cliente.subscribe(
            topico,
            subscription_name='consumidor-dinamico',
            # schema=None  # Sin schema definido
        )
        return consumidor
    
    def crear_consumer_con_schema_auto(self, topico):
        """Pulsar puede intentar auto-detectar el schema"""
        cliente = pulsar.Client('pulsar://localhost:6650')
        
        # 🔍 AUTO - Pulsar intenta detectar el schema automáticamente
        consumidor = cliente.subscribe(
            topico,
            subscription_name='consumidor-auto',
            schema=pulsar.schema.AutoConsumeSchema()
        )
        return consumidor
    
    async def procesar_mensaje_dinamico(self, mensaje):
        """Procesa mensaje determinando el schema dinámicamente"""
        try:
            # Opción 1: Usar .value() si hay schema
            try:
                datos = mensaje.value()
                schema_info = mensaje.schema_version()
                print(f"📋 Schema detectado: {schema_info}")
                return datos
            except Exception:
                pass
            
            # Opción 2: Fallback a JSON
            try:
                raw_data = mensaje.data().decode('utf-8')
                datos = json.loads(raw_data)
                print("📄 Interpretado como JSON")
                return datos
            except Exception:
                pass
            
            # Opción 3: Datos binarios puros
            print("🔧 Datos binarios - requiere interpretación manual")
            return mensaje.data()
            
        except Exception as e:
            print(f"❌ Error procesando mensaje: {e}")
            return None