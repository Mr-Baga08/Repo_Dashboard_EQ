import asyncio
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.client import Client as ClientModel
from app.models.token import Token as TokenModel
from app.models.trade import Trade as TradeModel, TradeStatus
from app.models.execution import Execution as ExecutionModel, ExecutionType
from app.schemas.order import OrderPayload, OrderResponse
from app.core.security import decrypt
from app.services.mofsl_api_service import MofslApiService

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/execute-all", response_model=List[OrderResponse])
async def execute_batch_order(payload: OrderPayload, db: Session = Depends(get_db)):
    """
    Executes a batch of orders for multiple clients simultaneously.
    """
    responses = []

    async def process_order(client_order):
        if client_order.quantity <= 0:
            return

        client = db.query(ClientModel).filter(ClientModel.id == client_order.client_id).first()
        if not client:
            responses.append(OrderResponse(mofsl_order_id="", client_id=client_order.client_id, status="ERROR", message="Client not found"))
            return

        token = db.query(TokenModel).filter(
            TokenModel.symbol == payload.token_symbol,
            TokenModel.exchange == payload.token_exchange
        ).first()
        if not token:
            responses.append(OrderResponse(mofsl_order_id="", client_id=client_order.client_id, status="ERROR", message="Token not found"))
            return

        try:
            decrypted_api_key = decrypt(client.api_key_encrypted)
            decrypted_api_secret = decrypt(client.api_secret_encrypted)
            
            # IMPORTANT: Hardcoding password and 2FA is insecure.
            # This is a placeholder for demonstration purposes.
            temp_password = "SOME_SECURE_PASSWORD"
            temp_2fa = "SOME_2FA_VALUE"

            mofsl_service = MofslApiService(
                api_key=decrypted_api_key,
                api_secret=decrypted_api_secret,
                client_id=client.client_id,
                password=temp_password,
                two_fa=temp_2fa,
            )

            order_info = {
                "clientcode": client.client_id,
                "exchange": payload.token_exchange,
                "symbol": payload.token_symbol,
                "buyorsell": payload.buy_or_sell,
                "ordertype": payload.order_type,
                "producttype": payload.trade_type,
                "quantityinlot": client_order.quantity,
                "symboltoken": token.id, # Assuming token.id is the symboltoken
                # Add other required fields with defaults if necessary
                "price": 0, # For market order
                "triggerprice": 0,
                "disclosedquantity": 0,
            }

            order_result = mofsl_service.place_order(order_info)

            if order_result.get("status") == "SUCCESS":
                mofsl_order_id = order_result.get("uniqueorderid", "")
                
                # Create or update a Trade
                trade = db.query(TradeModel).filter(
                    TradeModel.client_id == client.id,
                    TradeModel.token_id == token.id,
                    TradeModel.status == TradeStatus.open
                ).first()

                if not trade:
                    trade = TradeModel(
                        client_id=client.id,
                        token_id=token.id,
                        status=TradeStatus.open,
                        quantity=0,
                        avg_entry_price=0,
                    )
                    db.add(trade)
                
                # Create an Execution
                execution = ExecutionModel(
                    trade_id=trade.id,
                    mofsl_order_id=mofsl_order_id,
                    type=ExecutionType.buy if payload.buy_or_sell == "BUY" else ExecutionType.sell,
                    quantity=client_order.quantity,
                    price=order_result.get("price", 0) # Use actual price from response if available
                )
                db.add(execution)
                db.commit()

                responses.append(OrderResponse(
                    mofsl_order_id=mofsl_order_id,
                    client_id=client.id,
                    status="SUCCESS",
                    message="Order placed successfully."
                ))
            else:
                responses.append(OrderResponse(
                    mofsl_order_id="",
                    client_id=client.id,
                    status="ERROR",
                    message=order_result.get("message", "Failed to place order.")
                ))

        except HTTPException as e:
            responses.append(OrderResponse(mofsl_order_id="", client_id=client_order.client_id, status="ERROR", message=e.detail))
        except Exception as e:
            responses.append(OrderResponse(mofsl_order_id="", client_id=client_order.client_id, status="ERROR", message=f"An unexpected error occurred: {e}"))

    # Run all order processing concurrently
    await asyncio.gather(*(process_order(order) for order in payload.client_orders))
    
    return responses
