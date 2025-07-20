import uuid
import enum
from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Enum, DECIMAL
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.orm import relationship
from .base import Base

class TradeStatus(enum.Enum):
    open = "open"
    closed = "closed"

class Trade(Base):
    __tablename__ = 'trades'

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(pgUUID(as_uuid=True), ForeignKey('clients.id'), nullable=False)
    token_id = Column(Integer, ForeignKey('tokens.id'), nullable=False)
    status = Column(Enum(TradeStatus), default=TradeStatus.open, nullable=False)
    quantity = Column(Integer, nullable=False)
    avg_entry_price = Column(DECIMAL, nullable=False)
    entry_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    exit_price = Column(DECIMAL, nullable=True)
    exit_timestamp = Column(DateTime, nullable=True)

    client = relationship("Client", back_populates="trades")
    token = relationship("Token", back_populates="trades")
    executions = relationship("Execution", back_populates="trade", cascade="all, delete-orphan")
