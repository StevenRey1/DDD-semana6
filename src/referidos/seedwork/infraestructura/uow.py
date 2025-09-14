from abc import ABC, abstractmethod
from enum import Enum

from seedwork.dominio.entidades import AgregacionRaiz
from pydispatch import dispatcher

import pickle


class Lock(Enum):
    OPTIMISTA = 1
    PESIMISTA = 2

class Batch:
    def __init__(self, operacion, lock: Lock, *args, **kwargs):
        self.operacion = operacion
        self.args = args
        self.lock = lock
        self.kwargs = kwargs

class UnidadTrabajo(ABC):

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    def _obtener_eventos(self, batches=None):
        batches = self.batches if batches is None else batches
        for batch in batches:
            for arg in batch.args:
                if isinstance(arg, AgregacionRaiz):
                    return arg.eventos
        return list()

    @abstractmethod
    def _limpiar_batches(self):
        raise NotImplementedError

    @abstractmethod
    def batches(self) -> list[Batch]:
        raise NotImplementedError

    @abstractmethod
    def savepoints(self) -> list:
        raise NotImplementedError                    

    def commit(self):
        self._publicar_eventos_post_commit()
        self._limpiar_batches()

    @abstractmethod
    def rollback(self, savepoint=None):
        self._limpiar_batches()
    
    @abstractmethod
    def savepoint(self):
        raise NotImplementedError

    def registrar_batch(self, operacion, *args, lock=Lock.PESIMISTA, **kwargs):
        batch = Batch(operacion, lock, *args, **kwargs)
        self.batches.append(batch)
        self._publicar_eventos_dominio(batch)

    def _publicar_eventos_dominio(self, batch):
        for evento in self._obtener_eventos(batches=[batch]):
            dispatcher.send(signal=f'{type(evento).__name__}Dominio', evento=evento)

    def _publicar_eventos_post_commit(self):
        for evento in self._obtener_eventos():
            dispatcher.send(signal=f'{type(evento).__name__}Integracion', evento=evento)

def is_flask():
    try:
        from flask import session
        return True
    except Exception as e:
        return False

def registrar_unidad_de_trabajo(serialized_obj):
    from config.uow import UnidadTrabajoSQLAlchemy
    from flask import session
    
    try:
        session['uow'] = serialized_obj
    except RuntimeError:
        # Si no hay contexto de sesión, no hacer nada
        pass

def flask_uow():
    from flask import session
    from config.uow import UnidadTrabajoSQLAlchemy
    try:
        if session.get('uow'):
            return session['uow']
        else:
            uow_serialized = pickle.dumps(UnidadTrabajoSQLAlchemy())
            registrar_unidad_de_trabajo(uow_serialized)
            return uow_serialized
    except RuntimeError:
        # Si no hay contexto de sesión, retornar UoW serializada directamente
        return pickle.dumps(UnidadTrabajoSQLAlchemy())

def unidad_de_trabajo() -> UnidadTrabajo:
    if is_flask():
        try:
            return pickle.loads(flask_uow())
        except RuntimeError:
            # Si no hay contexto Flask activo (ej: threads de consumidores)
            from config.uow import UnidadTrabajoSQLAlchemy
            return UnidadTrabajoSQLAlchemy()
    else:
        # Para casos no-Flask, crear directamente
        from config.uow import UnidadTrabajoSQLAlchemy
        return UnidadTrabajoSQLAlchemy()

def guardar_unidad_trabajo(uow: UnidadTrabajo):
    if is_flask():
        try:
            registrar_unidad_de_trabajo(pickle.dumps(uow))
        except RuntimeError:
            # Si no hay contexto Flask activo, no hacemos nada
            # La UoW se manejará directamente en el thread
            pass
    else:
        # Para casos no-Flask, no necesitamos persistir en sesión
        pass


class UnidadTrabajoPuerto:

    @staticmethod
    def commit():
        uow = unidad_de_trabajo()
        uow.commit()
        guardar_unidad_trabajo(uow)

    @staticmethod
    def rollback(savepoint=None):
        uow = unidad_de_trabajo()
        uow.rollback(savepoint=savepoint)
        guardar_unidad_trabajo(uow)

    @staticmethod
    def savepoint():
        uow = unidad_de_trabajo()
        uow.savepoint()
        guardar_unidad_trabajo(uow)

    @staticmethod
    def dar_savepoints():
        uow = unidad_de_trabajo()
        return uow.savepoints()

    @staticmethod
    def registrar_batch(operacion, *args, lock=Lock.PESIMISTA, **kwargs):
        uow = unidad_de_trabajo()
        uow.registrar_batch(operacion, *args, lock=lock, **kwargs)
        guardar_unidad_trabajo(uow)

    @staticmethod
    def repositorio_referidos():
        from modulos.referidos.infraestructura.repositorios import RepositorioReferidosPostgreSQL
        return RepositorioReferidosPostgreSQL()
