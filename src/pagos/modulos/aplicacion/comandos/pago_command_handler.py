from seedworks.aplicacion.comandos import ejecutar_commando
from .base import PagoBaseHandler
from .pago_command import PagoCommand, TipoComandoPago
from ...infraestructura.repositorio_postgresql import RepositorioPagosPG, PagoORM
from config.pulsar_config import Settings
from pulsar import Client
from pulsar.schema import AvroSchema
from schema.eventos_pagos import ProcesarPago as PagoProcesadoSchema
import json
from datetime import datetime
from uuid import uuid4
import time
class PagoCommandHandler(PagoBaseHandler):
    """
    Handler unificado para PagoCommand.
    Maneja tanto comando 'Iniciar' como 'Cancelar' según especificación.
    """
    
    def handle(self, comando: PagoCommand):
        print(f"🔄 Ejecutando PagoCommandHandler - Comando: {comando.comando}")

        if comando.data.monto <= 500:
            return self._completar_pago(comando)

        
        if comando.comando == TipoComandoPago.INICIAR:
            return self._iniciar_pago(comando)
        elif comando.comando == TipoComandoPago.CANCELAR:
            return self._cancelar_pago(comando)
        elif comando.comando == TipoComandoPago.COMPLETAR:
            return self._completar_pago(comando)
        else:
            raise ValueError(f"Comando no soportado: {comando.comando}")
    
    def _iniciar_pago(self, comando: PagoCommand):
        """Lógica para iniciar un pago"""
        settings = Settings()
        repo = RepositorioPagosPG(settings.DB_URL)
        
        with repo.SessionLocal() as session:
            # Verificar si ya existe
            pago_existente = session.query(PagoORM).filter_by(
                idEvento=comando.data.idEvento
            ).first()
            
            if pago_existente:
                print(f"⚠️ Pago ya existe para evento {comando.data.idEvento}")
                return pago_existente
            
            # Crear nuevo pago
            idPago = str(uuid4())
            pago_orm = PagoORM(
                idPago=idPago,
                idEvento=comando.data.idEvento,
                idSocio=comando.data.idSocio,
                monto=comando.data.monto,
                estado="solicitado",
                fechaEvento=comando.data.fechaEvento,
                idTransaction=comando.idTransaction
            )
            session.add(pago_orm)
            session.commit()
            
            # Publicar evento PagoProcesado
            self._publicar_evento_procesado(repo, pago_orm, comando.idTransaction, "solicitado")
            print(f"✅ Pago {idPago} iniciado exitosamente")
            
            return pago_orm
    
    def _cancelar_pago(self, comando: PagoCommand):
        """Lógica para cancelar un pago"""
        settings = Settings()
        repo = RepositorioPagosPG(settings.DB_URL)
        
        with repo.SessionLocal() as session:
            # Buscar pago existente
            pago_existente = session.query(PagoORM).filter_by(
                idEvento=comando.data.idEvento
            ).first()
            
            if not pago_existente:
                raise ValueError(f"Pago no encontrado para evento {comando.data.idEvento}")
            
            # Cancelar pago
            pago_existente.estado = "rechazado"
            session.commit()
            
            # Publicar evento PagoProcesado
            self._publicar_evento_procesado(repo, pago_existente, comando.idTransaction, "rechazado")
            print(f"✅ Pago {pago_existente.idPago} cancelado exitosamente")
            
            return pago_existente

    def _completar_pago(self, comando: PagoCommand):
        """Lógica para completar un pago (transición a estado 'completado')."""
        settings = Settings()
        repo = RepositorioPagosPG(settings.DB_URL)

        with repo.SessionLocal() as session:
            pago_existente = session.query(PagoORM).filter_by(
                idEvento=comando.data.idEvento
            ).first()

            if not pago_existente:
                raise ValueError(f"Pago no encontrado para evento {comando.data.idEvento}")

            if pago_existente.estado == "completado":
                print(f"ℹ️ Pago {pago_existente.idPago} ya estaba completado")
                return pago_existente

            if pago_existente.estado == "rechazado":
                raise ValueError(f"No se puede completar un pago rechazado (idPago={pago_existente.idPago})")

            pago_existente.estado = "completado"
            pago_existente.fechaEvento = datetime.utcnow()
            session.commit()

            self._publicar_evento_procesado(repo, pago_existente, comando.idTransaction, "completado")
            print(f"✅ Pago {pago_existente.idPago} completado exitosamente")
            return pago_existente
    
    def _publicar_evento_procesado(self, repo, pago, idTransaction, estado):
        """Publica evento PagoProcesado directamente a Pulsar (sin outbox) con retries simples."""

        settings = Settings()
        client = Client(settings.PULSAR_URL)
        producer = client.create_producer(settings.TOPIC_PAGOS, schema=AvroSchema(PagoProcesadoSchema))
        try:
            record = PagoProcesadoSchema(
                idTransaction=idTransaction,
                idPago=pago.idPago,
                idEvento=pago.idEvento,
                idSocio=pago.idSocio,
                monto=float(pago.monto),
                fechaEvento=pago.fechaEvento,
                estado=estado
            )
            intentos = 0
            max_intentos = 3
            backoff = 0.5
            while True:
                try:
                    producer.send(record)
                    print(f"📤 Evento PagoProcesado publicado idPago={pago.idPago} estado={estado}")
                    break
                except Exception as e:
                    intentos += 1
                    if intentos >= max_intentos:
                        print(f"❌ Fallo publicando evento PagoProcesado tras {intentos} intentos: {e}")
                        break
                    time.sleep(backoff)
                    backoff *= 2
        finally:
            producer.close()
            client.close()

# Registrar handler usando singledispatch
@ejecutar_commando.register(PagoCommand)
def ejecutar_pago_command(comando: PagoCommand):
    handler = PagoCommandHandler()
    return handler.handle(comando)