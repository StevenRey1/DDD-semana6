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
        print(f"🔄 [UoW] Iniciando commit con {len(self.batches)} batches")
        
        try:
            for i, batch in enumerate(self.batches):
                print(f"🔄 [UoW] Ejecutando batch {i+1}: {batch.operacion.__name__}")
                lock = batch.lock
                batch.operacion(*batch.args, **batch.kwargs)
                print(f"✅ [UoW] Batch {i+1} ejecutado exitosamente")

            print("🔄 [UoW] Haciendo commit de la sesión de BD...")
            db.session.commit()
            print("✅ [UoW] Commit de BD exitoso!")

            super().commit()
            
        except Exception as e:
            print(f"❌ [UoW] Error en commit: {e}")
            print(f"❌ [UoW] Haciendo rollback...")
            db.session.rollback()
            raise

    def rollback(self, savepoint=None):
        if savepoint:
            savepoint.rollback()
        else:
            db.session.rollback()
        
        super().rollback()
    
    def registrar_batch(self, operacion, *args, lock=None, **kwargs):
        print(f"🔄 [UoW] registrar_batch llamado - operacion: {operacion.__name__}")
        print(f"🔄 [UoW] args: {args}")
        
        from seedwork.infraestructura.uow import Batch, Lock
        if lock is None:
            lock = Lock.PESIMISTA
            
        batch = Batch(operacion, lock, *args, **kwargs)
        self._batches.append(batch)
        print(f"✅ [UoW] Batch agregado - Total batches: {len(self._batches)}")
        
        # Llamar al método padre para eventos de dominio
        try:
            self._publicar_eventos_dominio(batch)
        except Exception as e:
            print(f"⚠️ [UoW] Error publicando eventos de dominio: {e}")

    def _publicar_eventos_dominio(self, batch):
        """Método copiado del padre para publicar eventos de dominio"""
        from pydispatch import dispatcher
        eventos = self._obtener_eventos(batches=[batch])
        for evento in eventos:
            dispatcher.send(signal=f'{type(evento).__name__}Dominio', evento=evento)
    
    def _obtener_eventos(self, batches=None):
        """Método copiado del padre para obtener eventos"""
        from seedwork.dominio.entidades import AgregacionRaiz
        batches = self.batches if batches is None else batches
        eventos = []
        for batch in batches:
            for arg in batch.args:
                if isinstance(arg, AgregacionRaiz):
                    eventos.extend(arg.eventos)
        return eventos
    
    def savepoint(self):
        db.session.begin_nested()