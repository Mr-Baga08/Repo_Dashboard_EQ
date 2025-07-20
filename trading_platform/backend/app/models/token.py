from sqlalchemy import Column, Integer, String, Text, Sequence
from sqlalchemy.orm import relationship
from .base import Base

class Token(Base):
    __tablename__ = 'tokens'

    id = Column(Integer, Sequence('token_id_seq'), primary_key=True)
    symbol = Column(String, unique=True, index=True, nullable=False)
    exchange = Column(String, nullable=False)
    description = Column(Text)

    trades = relationship("Trade", back_populates="token")
