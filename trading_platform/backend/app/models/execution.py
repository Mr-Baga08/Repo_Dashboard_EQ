import uuid
import enum
from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Enum, DECIMAL
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.orm import relationship
from .base import Base

class ExecutionType(enum.Enum):
    buy = "buy"
    sell = "sell"

class Execution(Base):
    __tablename__ = 'executions'

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trade_id = Column(pgUUID(as_uuid=True), ForeignKey('trades.id'), nullable=False)
    mofsl_order_id = Column(String, unique=True, nullable=False)
    type = Column(Enum(ExecutionType), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(DECIMAL, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    trade = relationship("Trade", back_populates="executions")
