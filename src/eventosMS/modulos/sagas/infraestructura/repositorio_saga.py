from eventosMS.config.db import db
from .modelos import SagaInstance, SagaStepLog
from datetime import datetime
from typing import Optional

class RepositorioSaga:
    def crear_o_recuperar_saga(self, nombre: str, correlacion_id: str, total_pasos: int) -> SagaInstance:
        instancia = SagaInstance.query.filter_by(nombre=nombre, correlacion_id=correlacion_id).first()
        if instancia:
            return instancia
        instancia = SagaInstance(nombre=nombre, correlacion_id=correlacion_id, total_pasos=total_pasos, estado='RUNNING', paso_actual=0)
        db.session.add(instancia)
        db.session.commit()
        return instancia

    def registrar_step(self, saga_id: str, paso: int, nombre_paso: str, accion: str, estado: str, detalle: Optional[str] = None):
        step = SagaStepLog(saga_id=saga_id, paso=paso, nombre_paso=nombre_paso, accion=accion, estado=estado, detalle=detalle)
        db.session.add(step)
        db.session.commit()
        return step

    def actualizar_estado_saga(self, saga_id: str, estado: str, paso_actual: Optional[int] = None, finalizada: bool = False):
        instancia = SagaInstance.query.get(saga_id)
        if not instancia:
            return
        instancia.estado = estado
        if paso_actual is not None:
            instancia.paso_actual = paso_actual
        if finalizada:
            instancia.finalizada_en = datetime.utcnow()
        db.session.commit()
        return instancia

    def obtener_por_correlacion(self, nombre: str, correlacion_id: str) -> Optional[SagaInstance]:
        return SagaInstance.query.filter_by(nombre=nombre, correlacion_id=correlacion_id).first()

    def listar_pasos(self, saga_id: str):
        return SagaStepLog.query.filter_by(saga_id=saga_id).order_by(SagaStepLog.timestamp.asc()).all()
