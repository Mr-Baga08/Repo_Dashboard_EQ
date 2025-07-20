import uuid
from sqlalchemy import Column, String, LargeBinary, DateTime, func
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.orm import relationship
from .base import Base

class Client(Base):
    __tablename__ = 'clients'

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    api_key_encrypted = Column(LargeBinary, nullable=False)
    api_secret_encrypted = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    trades = relationship("Trade", back_populates="client")
