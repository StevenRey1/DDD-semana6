import time
import os
import datetime
import requests
import json
from fastavro.schema import parse_schema
from pulsar.schema import *

epoch = datetime.datetime.utcfromtimestamp(0)
PULSAR_ENV: str = 'BROKER_HOST'

def time_millis():
    return int(time.time() * 1000)

def unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0

def millis_a_datetime(millis):
    return datetime.datetime.fromtimestamp(millis/1000.0)

def broker_host():
    return os.getenv(PULSAR_ENV, default="localhost")

def consultar_schema_registry(topico: str) -> dict:
    try:
        response = requests.get(f'http://{broker_host()}:8080/admin/v2/schemas/{topico}/schema')
        if response.status_code == 200:
            json_registry = response.json()
            data = json_registry.get('data')
            if isinstance(data, str):
                return json.loads(data)
            elif isinstance(data, dict):
                return data
            else:
                return {}
        else:
            print(f"Schema Registry returned status {response.status_code}")
            return {}
    except Exception as e:
        print(f"Error consulting Schema Registry: {e}")
        return {}

def obtener_schema_avro_de_diccionario(json_schema: dict) -> AvroSchema:
    try:
        print(f"Schema to parse: {json_schema}")
        definicion_schema = parse_schema(json_schema)
        return AvroSchema(None, schema_definition=definicion_schema)
    except Exception as e:
        print(f"Error parsing schema: {e}")
        print(f"Schema content: {json_schema}")
        # Fallback: create a basic schema if parsing fails
        basic_schema = {
            "type": "record",
            "name": "BasicRecord",
            "fields": [
                {"name": "message", "type": "string"}
            ]
        }
        definicion_schema = parse_schema(basic_schema)
        return AvroSchema(None, schema_definition=definicion_schema)

