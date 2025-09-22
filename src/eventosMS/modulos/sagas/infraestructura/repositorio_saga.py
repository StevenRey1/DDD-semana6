from config.db import db
from eventosMS.modulos.sagas.infraestructura.modelos import SagaLog
import uuid

class RepositorioSaga:
    def __init__(self, app):
        self.app = app

    def _insertar(self, *, tipo, nombre, paso, estado, id_transaction):
        with self.app.app_context():  # 👈 aseguramos el contexto
            entry = SagaLog(
                id=str(uuid.uuid4()),
                id_transaction=id_transaction,
                tipo=tipo,
                nombre=nombre,
                paso=paso,
                estado=estado
            )
            db.session.add(entry)
            db.session.commit()
            return entry

    def registrar_inicio(self, id_transaction):
        return self._insertar(
            tipo='inicio',
            nombre='Inicio',
            paso=0,
            estado='RUNNING',
            id_transaction=id_transaction
        )

    def registrar_fin(self, id_transaction, paso, exito=True):
        return self._insertar(
            tipo='fin',
            nombre='Fin',
            paso=paso,
            estado='COMPLETED' if exito else 'FAILED',
            id_transaction=id_transaction
        )

    def registrar_comando(self, id_transaction, nombre, paso, pendiente=True):
        return self._insertar(
            tipo='comando',
            nombre=nombre,
            paso=paso,
            estado='PENDING' if pendiente else 'RUNNING',
            id_transaction=id_transaction
        )

    def registrar_evento_ok(self, id_transaction, nombre, paso):
        return self._insertar(
            tipo='evento_ok',
            nombre=nombre,
            paso=paso,
            estado='OK',
            id_transaction=id_transaction
        )

    def registrar_evento_error(self, id_transaction, nombre, paso):
        return self._insertar(
            tipo='evento_error',
            nombre=nombre,
            paso=paso,
            estado='ERROR',
            id_transaction=id_transaction
        )

    def ultimo(self, id_transaction):
        with self.app.app_context():
            return (
                SagaLog.query.filter_by(id_transaction=id_transaction)
                .order_by(SagaLog.timestamp.desc())
                .first()
            )
