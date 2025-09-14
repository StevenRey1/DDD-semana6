from config.db import db
from seedwork.infraestructura.uow import UnidadTrabajo, Batch

class UnidadTrabajoSQLAlchemy(UnidadTrabajo):

    def __init__(self):
        self._batches: list[Batch] = list()

    def __enter__(self) -> UnidadTrabajo:
        return super().__enter__()

    def __exit__(self, *args):
        self.rollback()

    def _limpiar_batches(self):
        self._batches = list()

    @property
    def savepoints(self) -> list:
        return list[db.session.get_nested_transaction()]

    @property
    def batches(self) -> list[Batch]:
        return self._batches             

    def commit(self):
        print("DEBUG: Inside UnidadTrabajoSQLAlchemy.commit")
        for batch in self.batches:
            lock = batch.lock
            print(f"DEBUG: Executing batch operation: {batch.operacion.__name__} with args {batch.args}")
            batch.operacion(*batch.args, **batch.kwargs)

        print("DEBUG: Calling db.session.commit()")
        db.session.commit()
        print("DEBUG: db.session.commit() finished")

        super().commit()

    def rollback(self, savepoint=None):
        if savepoint:
            savepoint.rollback()
        else:
            db.session.rollback()
        
        super().rollback()
    
    def savepoint(self):
        db.session.begin_nested()
