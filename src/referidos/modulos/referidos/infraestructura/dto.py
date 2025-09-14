from config.db import db
import datetime

class Referido(db.Model):
    __tablename__ = "referidos"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.String, primary_key=True)
    id_socio = db.Column(db.String, nullable=False)
    id_evento = db.Column(db.String, nullable=False)
    tipo_evento = db.Column(db.String, nullable=False)
    id_referido = db.Column(db.String, nullable=False)
    monto = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String, nullable=False)
    fecha_evento = db.Column(db.DateTime, nullable=False)
