import typing
import strawberry
import uuid
import requests
import os

from datetime import datetime
from typing import Optional


AEROALPES_HOST = os.getenv("AEROALPES_ADDRESS", default="localhost")
FORMATO_FECHA = '%Y-%m-%dT%H:%M:%SZ'
FORMATO_FECHA_HTTP = '%a, %d %b %Y %H:%M:%S %Z'

def parsear_fecha(fecha_str):
    """
    Intenta parsear fechas en múltiples formatos
    """
    if not fecha_str:
        return datetime.now()
    
    # Lista de formatos de fecha a intentar
    formatos = [
        '%Y-%m-%dT%H:%M:%SZ',           # ISO format: 2025-09-21T23:14:40Z
        '%a, %d %b %Y %H:%M:%S %Z',     # HTTP format: Sun, 21 Sep 2025 23:14:40 GMT
        '%Y-%m-%d %H:%M:%S',            # Simple format: 2025-09-21 23:14:40
        '%Y-%m-%dT%H:%M:%S.%fZ',        # ISO with microseconds
    ]
    
    for formato in formatos:
        try:
            return datetime.strptime(fecha_str, formato)
        except ValueError:
            continue
    
    # Si ningún formato funciona, usar la fecha actual
    print(f"⚠️ No se pudo parsear fecha: {fecha_str}, usando fecha actual")
    return datetime.now()

def obtener_reservas(root) -> typing.List["Reserva"]:
    reservas_json = requests.get(f'http://{AEROALPES_HOST}:5000/vuelos/reserva').json()
    reservas = []

    for reserva in reservas_json:
        reservas.append(
            Reserva(
                fecha_creacion=parsear_fecha(reserva.get('fecha_creacion')), 
                fecha_actualizacion=parsear_fecha(reserva.get('fecha_actualizacion')), 
                id=reserva.get('id'), 
                id_usuario=reserva.get('id_usuario', '')
            )
        )

    return reservas

@strawberry.type
class Itinerario:
    # TODO Completar objeto strawberry para incluir los itinerarios
    ...

@strawberry.type
class Reserva:
    id: str
    id_usuario: str
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    #itinerarios: typing.List[Itinerario]

@strawberry.type
class ReservaRespuesta:
    mensaje: str
    codigo: int


def obtener_eventos_socio(root, idSocio: str) -> "EventosList":
    EVENTOSMS_HOST = os.getenv("EVENTOSMS_ADDRESS", default="eventos")
    url = f'http://{EVENTOSMS_HOST}:8003/eventos/{idSocio}'
    print(f"🔗 BFF: Consultando eventos en URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Lanza excepción si hay error HTTP
        eventos_json = response.json()
        print(f"📨 BFF: Respuesta exitosa de eventosMS: {len(eventos_json.get('eventos', []))} eventos")
    except requests.exceptions.RequestException as e:
        print(f"❌ BFF: Error conectando con eventosMS: {e}")
        # Devolver lista vacía en caso de error
        return EventosList(
            idSocio=idSocio,
            eventos=[]
        )
    
    eventos = []

    for i, evento in enumerate(eventos_json.get('eventos', [])):
        print(f"📋 BFF: Procesando evento {i+1}: {evento}")
        
        # Validar y limpiar todos los campos
        id_evento = evento.get('idEvento') or f"evento-{i+1}"
        id_referido = evento.get('idReferido') or "N/A"
        id_socio_evento = evento.get('idSocio') or idSocio  # idSocio no viene en cada evento, usar el de la consulta
        monto_evento = evento.get('monto')
        if monto_evento is None:
            monto_evento = 0.0
        else:
            monto_evento = float(monto_evento)
        
        fecha_evento = parsear_fecha(evento.get('fechaEvento'))
        estado_evento = evento.get('estado') or evento.get('estado_evento') or "pendiente"  # Intentar ambos campos
        print(f"🔍 BFF: Campo estado del evento {i+1}: '{evento.get('estado')}' -> mapeado a: '{estado_evento}'")
        ganancia_evento = evento.get('ganancia')
        if ganancia_evento is None:
            ganancia_evento = 0.0
        else:
            ganancia_evento = float(ganancia_evento)
        
        print(f"🏗️  BFF: Creando EventoItem {i+1} con estadoEvento='{estado_evento}'")
        
        eventos.append(
            EventoItem(
                idEvento=id_evento,
                idReferido=id_referido,
                idSocio=id_socio_evento,
                monto=monto_evento,
                fechaEvento=fecha_evento,
                estadoEvento=estado_evento,
                ganancia=ganancia_evento
            )
        )

    return EventosList(
        idSocio=eventos_json.get('idSocio', ''),
        eventos=eventos
    )

def obtener_referidos_socio(root, idSocio: str) -> "ReferidosList":
    REFERIDOS_HOST = os.getenv("REFERIDOS_ADDRESS", default="referidos")
    url = f'http://{REFERIDOS_HOST}:8004/referidos/{idSocio}'
    print(f"🔗 BFF: Consultando referidos en URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Lanza excepción si hay error HTTP
        referidos_json = response.json()
        print(f"📨 BFF: Respuesta exitosa de referidosMS: {len(referidos_json.get('referidos', []))} referidos")
    except requests.exceptions.RequestException as e:
        print(f"❌ BFF: Error conectando con referidosMS: {e}")
        # Devolver lista vacía en caso de error
        return ReferidosList(
            idSocio=idSocio,
            referidos=[]
        )
    
    referidos = []

    for i, referido in enumerate(referidos_json.get('referidos', [])):
        print(f"📋 BFF: Procesando referido {i+1}: {referido}")
        
        # Validar y limpiar todos los campos
        id_evento = referido.get('idEvento') or f"referido-{i+1}"
        id_referido = referido.get('idReferido') or "N/A"
        tipo_evento = referido.get('tipoEvento') or "venta_creada"
        monto_referido = referido.get('monto')
        if monto_referido is None:
            monto_referido = 0.0
        else:
            monto_referido = float(monto_referido)
        
        fecha_referido = parsear_fecha(referido.get('fechaEvento'))
        estado_referido = referido.get('estado_evento') or referido.get('estado') or "pendiente"  # Intentar ambos campos
        print(f"🔍 BFF: Campo estado del referido {i+1}: '{referido.get('estado_evento')}' -> mapeado a: '{estado_referido}'")
        
        print(f"🏗️  BFF: Creando ReferidoItem {i+1} con estadoEvento='{estado_referido}'")
        
        referidos.append(
            ReferidoItem(
                idEvento=id_evento,
                idReferido=id_referido,
                tipoEvento=tipo_evento,
                monto=monto_referido,
                fechaEvento=fecha_referido,
                estadoEvento=estado_referido
            )
        )

    return ReferidosList(
        idSocio=referidos_json.get('idSocio', idSocio),
        referidos=referidos
    )

def obtener_pago_info(root, idPago: str) -> "PagoInfo":
    PAGOS_HOST = os.getenv("PAGOS_ADDRESS", default="pagos")
    url = f'http://{PAGOS_HOST}:8080/pagos/{idPago}'
    print(f"🔗 BFF: Consultando pago en URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Lanza excepción si hay error HTTP
        pago_json = response.json()
        print(f"📨 BFF: Respuesta exitosa de pagosMS: {pago_json}")
    except requests.exceptions.RequestException as e:
        print(f"❌ BFF: Error conectando con pagosMS: {e}")
        # Devolver objeto vacío en caso de error
        return PagoInfo(
            idPago=idPago,
            idTransaction="Error",
            idSocio="Error",
            pago=0.0,
            estadoPago="error",
            fechaPago=datetime.now()
        )
    
    # Validar y limpiar todos los campos
    id_transaction = pago_json.get('idTransaction') or "N/A"
    id_pago = pago_json.get('idPago') or idPago
    id_socio = pago_json.get('idSocio') or "N/A"
    
    pago_monto = pago_json.get('pago')
    if pago_monto is None:
        pago_monto = 0.0
    else:
        pago_monto = float(pago_monto)
    
    fecha_pago = parsear_fecha(pago_json.get('fechaPago'))
    estado_pago = pago_json.get('estadoPago') or pago_json.get('estado_pago') or "pendiente"  # Intentar ambos campos
    print(f"🔍 BFF: Campo estado del pago: '{pago_json.get('estadoPago')}' -> mapeado a: '{estado_pago}'")
    
    print(f"🏗️  BFF: Creando PagoInfo con estadoPago='{estado_pago}'")
    
    return PagoInfo(
        idTransaction=id_transaction,
        idPago=id_pago,
        idSocio=id_socio,
        pago=pago_monto,
        estadoPago=estado_pago,
        fechaPago=fecha_pago
    )

@strawberry.type
class EventoItem:
    tipo_evento: str = strawberry.field(default="venta_creada")
    idEvento: str = strawberry.field(default="N/A")
    idReferido: str = strawberry.field(default="N/A") 
    idSocio: str = strawberry.field(default="N/A")
    monto: float = strawberry.field(default=0.0)
    fechaEvento: datetime = strawberry.field(default_factory=datetime.now)
    estadoEvento: Optional[str] = strawberry.field(default="pendiente")
    ganancia: float = strawberry.field(default=0.0)
    

@strawberry.type
class EventosList:
    idSocio: str
    eventos: typing.List[EventoItem]

@strawberry.type
class EventoRespuesta:
    mensaje: str
    codigo: int

@strawberry.type
class ReferidoItem:
    idEvento: str = strawberry.field(default="N/A")
    idReferido: str = strawberry.field(default="N/A")
    tipoEvento: str = strawberry.field(default="venta_creada")
    monto: float = strawberry.field(default=0.0)
    estadoEvento: Optional[str] = strawberry.field(default="pendiente")
    fechaEvento: datetime = strawberry.field(default_factory=datetime.now)

@strawberry.type
class ReferidosList:
    idSocio: str
    referidos: typing.List[ReferidoItem]

@strawberry.type
class PagoInfo:
    idTransaction: str = strawberry.field(default="N/A")
    idPago: str = strawberry.field(default="N/A")
    idSocio: str = strawberry.field(default="N/A")
    pago: float = strawberry.field(default=0.0)
    estadoPago: Optional[str] = strawberry.field(default="pendiente")
    fechaPago: datetime = strawberry.field(default_factory=datetime.now)






