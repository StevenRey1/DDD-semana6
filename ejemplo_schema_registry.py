"""
Ejemplo de uso de Schema Registry para compartir schemas
"""

import pulsar
from pulsar.schema import AvroSchema, Record, String, Float

class SchemaRegistryManager:
    """Gestor de Schema Registry para compartir schemas entre microservicios"""
    
    def __init__(self, pulsar_url='pulsar://localhost:6650'):
        self.cliente = pulsar.Client(pulsar_url)
        self.schemas_registrados = {}
    
    def registrar_schema(self, topico, schema_class, version="v1"):
        """Registra un schema en Pulsar para un tópico específico"""
        try:
            # Crear productor temporal para registrar el schema
            productor = self.cliente.create_producer(
                topico,
                schema=AvroSchema(schema_class),
                producer_name=f"schema-registry-{version}"
            )
            
            # El schema se registra automáticamente
            print(f"✅ Schema registrado para {topico}: {schema_class.__name__}")
            self.schemas_registrados[topico] = {
                'schema': schema_class,
                'version': version
            }
            
            productor.close()
            return True
            
        except Exception as e:
            print(f"❌ Error registrando schema para {topico}: {e}")
            return False
    
    def obtener_schema_de_topico(self, topico):
        """Obtiene el schema registrado de un tópico"""
        try:
            # Crear consumidor temporal para obtener schema info
            consumidor = self.cliente.subscribe(
                topico,
                subscription_name='schema-reader-temp',
                schema=pulsar.schema.AutoConsumeSchema()
            )
            
            # Intentar leer un mensaje para obtener schema info
            try:
                mensaje = consumidor.receive(timeout_millis=1000)
                schema_info = mensaje.schema_version()
                print(f"📋 Schema encontrado en {topico}: {schema_info}")
                consumidor.acknowledge(mensaje)
                consumidor.close()
                return schema_info
            except pulsar.Timeout:
                print(f"⚠️ No hay mensajes en {topico} para determinar schema")
                consumidor.close()
                return None
                
        except Exception as e:
            print(f"❌ Error obteniendo schema de {topico}: {e}")
            return None


# Ejemplo de uso
def ejemplo_schema_registry():
    """Ejemplo de cómo usar Schema Registry"""
    
    # 1. Definir schema compartido
    class EventoCompartido(Record):
        id = String()
        tipo = String()
        datos = String()
    
    # 2. Crear manager
    manager = SchemaRegistryManager()
    
    # 3. Registrar schema
    manager.registrar_schema('eventos-compartidos', EventoCompartido)
    
    # 4. Otros servicios pueden obtener el schema
    schema_info = manager.obtener_schema_de_topico('eventos-compartidos')
    
    return schema_info


if __name__ == "__main__":
    ejemplo_schema_registry()