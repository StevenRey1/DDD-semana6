import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from config.db import db
class SagaLog(db.Model):
    __tablename__ = 'saga_log'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    id_transaction = db.Column(db.String(120), nullable=False)
    tipo = db.Column(db.String(40), nullable=False)      # inicio, evento_ok, evento_error, comando, fin, debug
    nombre = db.Column(db.String(120), nullable=False)   # CrearEvento, ReferidoCommand, etc.
    paso = db.Column(db.Integer, nullable=True) # index del paso 
    estado = db.Column(db.String(30), nullable=False)    # RUNNING, OK, ERROR, COMPLETED, FAILED, PENDING
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)