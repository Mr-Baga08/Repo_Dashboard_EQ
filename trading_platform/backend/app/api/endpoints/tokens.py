from typing import List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.db.session import SessionLocal
from app.models.client import Client as ClientModel
from app.models.trade import Trade as TradeModel, TradeStatus
from app.models.token import Token as TokenModel

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{token_symbol}/holders", response_model=List[Dict[str, Any]])
async def get_token_holders(
    token_symbol: str,
    token_exchange: str, # Assuming exchange is also needed to uniquely identify a token
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of clients holding open positions for a specific token.
    """
    token = db.query(TokenModel).filter(
        and_(TokenModel.symbol == token_symbol, TokenModel.exchange == token_exchange)
    ).first()

    if not token:
        raise HTTPException(status_code=404, detail=f"Token {token_symbol} on {token_exchange} not found.")

    # Query for open trades of this token and join with client details
    token_holders = db.query(ClientModel, TradeModel).join(TradeModel).filter(
        and_(
            TradeModel.token_id == token.id,
            TradeModel.status == TradeStatus.open
        )
    ).all()

    result = []
    for client, trade in token_holders:
        result.append({
            "client_id": str(client.id), # Convert UUID to string for JSON serialization
            "client_name": client.name,
            "quantity_held": trade.quantity,
            "avg_price": float(trade.avg_entry_price), # Convert Decimal to float
        })
    
    return result
