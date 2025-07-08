from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Float,
    BigInteger,
)
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import config

Base = declarative_base()
engine = create_engine(config.DATABASE_URI)
SessionLocal = sessionmaker(bind=engine)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    account_name = Column(String)
    order_datetime = Column(DateTime)
    bank = Column(String)
    amount = Column(Float)
    recipient_details = Column(String)  # Реквизит получателя
    paylonium_id = Column(
        String, unique=True, nullable=False
    )  # Уникальный номер заявки с ПЛ

    def __repr__(self):
        return f"<Order(id={self.id}, pl_id='{self.paylonium_id}', account='{self.account_name}')>"


def init_db():
    """Создает таблицы в БД"""
    Base.metadata.create_all(engine)


def add_order(session: Session, order_data: dict):
    """Добавляет новую заявку в БД"""
    new_order = Order(
        account_name=order_data["account_name"],
        order_datetime=datetime.strptime(order_data["datetime"], "%Y-%m-%d %H:%M:%S"),
        bank=order_data["bank"],
        amount=order_data["amount"],
        recipient_details=order_data["recipient_details"],
        paylonium_id=order_data["paylonium_id"],
    )
    session.add(new_order)
    session.commit()
    print(
        f"Сохранена заявка {new_order.paylonium_id} для аккаунта {new_order.account_name}"
    )


def order_exists(session: Session, paylonium_id):
    """Проверяет, существует ли заявка с таким ID в БД"""
    return (
        session.query(Order).filter(Order.paylonium_id == paylonium_id).first()
        is not None
    )
