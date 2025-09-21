from eventosMS.config.db import db
from .modelos import SagaLog
import uuid
from typing import Optional


class RepositorioSaga:
    """Repositorio mínimo (pedagógico) para registrar la evolución de una sola saga.

    Decisión: solo una saga -> la columna 'nombre' almacena directamente el nombre
    del evento, comando o marcador (Inicio, Fin, CrearEvento, ReferidoCommand, etc.).
    No usamos 'detalle'.
    """

    def _insertar(self, *, tipo: str, nombre: str, paso: int | None, estado: str, id_transaction: str):
        entry = SagaLog(
            id=str(uuid.uuid4()),
            nombre=nombre,              # Aquí guardamos el nombre dinámico del evento/comando
            id_transaction=id_transaction,
            tipo=tipo,
            paso=paso,
            estado=estado
        )
        db.session.add(entry)
        db.session.commit()
        return entry

    # ------------------ Helpers de registro ------------------ #
    def registrar_inicio(self, id_transaction: str):
        return self._insertar(tipo='inicio', nombre='Inicio', paso=0, estado='RUNNING', id_transaction=id_transaction)

    def registrar_evento_ok(self, id_transaction: str, nombre_evento: str, paso: int):
        return self._insertar(tipo='evento_ok', nombre=nombre_evento, paso=paso, estado='OK', id_transaction=id_transaction)

    def registrar_evento_error(self, id_transaction: str, nombre_evento: str, paso: int):
        return self._insertar(tipo='evento_error', nombre=nombre_evento, paso=paso, estado='ERROR', id_transaction=id_transaction)

    def registrar_comando(self, id_transaction: str, nombre_comando: str, paso: int, pendiente: bool = True):
        estado = 'PENDING' if pendiente else 'OK'
        return self._insertar(tipo='comando', nombre=nombre_comando, paso=paso, estado=estado, id_transaction=id_transaction)

    def registrar_fin(self, id_transaction: str, paso: int, exito: bool = True):
        estado = 'COMPLETED' if exito else 'FAILED'
        return self._insertar(tipo='fin', nombre='Fin', paso=paso, estado=estado, id_transaction=id_transaction)

    # ------------------ Consultas ------------------ #



