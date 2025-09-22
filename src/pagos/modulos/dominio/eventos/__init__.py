"""Eventos de dominio de pagos.

Contrato simplificado: sólo se utiliza el evento de integración/domain bridge `PagoProcesado`.
Se removieron eventos previos PagoSolicitado, PagoCompletado y PagoRechazado.
"""
from .pagos import PagoProcesado

__all__ = ["PagoProcesado"]
