from pydantic import BaseModel
from uuid import UUID
from typing import List

class OrderExecutionPayload(BaseModel):
    client_id: UUID
    quantity: int

class OrderPayload(BaseModel):
    token_symbol: str
    token_exchange: str
    trade_type: str  # e.g., 'MTF' or 'INTRADAY'
    order_type: str  # e.g., 'MARKET'
    buy_or_sell: str # e.g., 'BUY' or 'SELL'
    client_orders: List[OrderExecutionPayload]

class OrderResponse(BaseModel):
    mofsl_order_id: str
    client_id: UUID
    status: str
    message: str
