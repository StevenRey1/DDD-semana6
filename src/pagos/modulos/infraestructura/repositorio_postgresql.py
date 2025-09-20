from sqlalchemy import create_engine, Column, String, Float, DateTime, Numeric
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from ..dominio.entidades import Pago
from ..dominio.repositorios import RepoPagos

Base = declarative_base()

class PagoORM(Base):
    __tablename__ = "pagos"
    idPago = Column(String, primary_key=True)
    idEvento = Column(String, nullable=False)
    idSocio = Column(String, nullable=False)
    monto = Column(Numeric(18,2), nullable=False)
    estado = Column(String, nullable=False)
    fechaPago = Column(DateTime(timezone=True), nullable=False)
    idTransaction = Column(String, nullable=True)  # Nuevo campo según especificación


class RepositorioPagosPG(RepoPagos):
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url, future=True)
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False, class_=Session)
        Base.metadata.create_all(self.engine)

    def by_id(self, idPago: str) -> Optional[Pago]:
        with self.SessionLocal() as session:
            pago_orm = session.get(PagoORM, idPago)
            if pago_orm:
                return Pago(
                    idPago=pago_orm.idPago,
                    idEvento=pago_orm.idEvento,
                    idSocio=pago_orm.idSocio,
                    monto=float(pago_orm.monto),
                    estado=pago_orm.estado,
                    fechaPago=pago_orm.fechaPago,
                    idTransaction=pago_orm.idTransaction
                )
            return None

    def guardar(self, pago: Pago) -> None:
        with self.SessionLocal() as session:
            pago_orm = session.get(PagoORM, pago.idPago)
            if pago_orm:
                pago_orm.estado = pago.estado
                pago_orm.fechaPago = pago.fechaPago
                pago_orm.idTransaction = pago.idTransaction
            else:
                pago_orm = PagoORM(
                    idPago=pago.idPago,
                    idEvento=pago.idEvento,
                    idSocio=pago.idSocio,
                    monto=pago.monto,
                    estado=pago.estado,
                    fechaPago=pago.fechaPago,
                    idTransaction=pago.idTransaction
                )
                session.add(pago_orm)
            session.commit()

    def init_db(self):
        Base.metadata.create_all(self.engine)
