import uuid
from datetime import datetime
from eventosMS.config.db import db

# Tabla principal de instancia de saga
class SagaInstance(db.Model):
    __tablename__ = 'saga_instance'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = db.Column(db.String(120), nullable=False)
    correlacion_id = db.Column(db.String(120), nullable=False)
    estado = db.Column(db.String(30), nullable=False, default='PENDING')
    paso_actual = db.Column(db.Integer, nullable=True)
    total_pasos = db.Column(db.Integer, nullable=False, default=0)
    iniciada_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    actualizada_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    finalizada_en = db.Column(db.DateTime, nullable=True)

    __table_args__ = (
        db.UniqueConstraint('nombre', 'correlacion_id', name='uq_saga_nombre_correlacion'),
    )

# Tabla de logs de pasos
class SagaStepLog(db.Model):
    __tablename__ = 'saga_step_log'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    saga_id = db.Column(db.String(36), db.ForeignKey('saga_instance.id'), nullable=False, index=True)
    paso = db.Column(db.Integer, nullable=False)
    nombre_paso = db.Column(db.String(120), nullable=False)
    accion = db.Column(db.String(40), nullable=False)  # publicar_comando | evento_ok | evento_error | inicio | fin
    estado = db.Column(db.String(30), nullable=False)  # PENDING | OK | ERROR
    detalle = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    saga = db.relationship('SagaInstance', backref=db.backref('steps', lazy=True))
