# Propósito: Definir los modelos de persistencia (SQLAlchemy) que representan las tablas 



"""DTOs (modelos de persistencia) para la capa de infraestructura del dominio"""

from config.db import db
import datetime

class Referido(db.Model):
    __tablename__ = "referidos"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.String, primary_key=True)
    idSocio = db.Column(db.String, nullable=False)
    idReferido = db.Column(db.String, nullable=False)
    estado = db.Column(db.String, nullable=False)
    idEvento = db.Column(db.String, nullable=False)
    monto = db.Column(db.Float, nullable=False)
    tipoEvento = db.Column(db.String, nullable=False)
    fechaEvento = db.Column(db.DateTime, nullable=False)
    fecha_creacion = db.Column(db.DateTime, nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
