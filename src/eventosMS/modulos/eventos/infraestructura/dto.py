"""
DTOs de infraestructura para el módulo de Eventos
"""
from sqlalchemy import Column, String, DateTime, Integer, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from config.db import db
import uuid


class EventoEntity(db.Model):
    """
    Entidad de base de datos para eventos
    """
    __tablename__ = 'eventos'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_socio = Column(UUID(as_uuid=True), nullable=False)
    id_referido = Column(UUID(as_uuid=True), nullable=True)
    tipo = Column(String(100), nullable=False)
    estado = Column(String(50), nullable=False, default='pendiente')
    monto = Column(db.Float, nullable=True)
    ganancia = Column(db.Float, nullable=False, default=0.0)
    fecha_creacion = Column(DateTime, nullable=False, index=True)
    fecha_evento = Column(DateTime, nullable=False)   