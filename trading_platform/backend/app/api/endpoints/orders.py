from typing import List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime

from app.db.session import SessionLocal
from app.models.client import Client as ClientModel
from app.models.trade import Trade as TradeModel, TradeStatus
from app.models.execution import Execution as ExecutionModel, ExecutionType
from app.models.token import Token as TokenModel
from app.schemas.order import OrderPayload, OrderResponse, TokenExitPayload
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

@router.post("/execute-all", response_model=List[OrderResponse], status_code=status.HTTP_200_OK)
async def execute_all_orders(order_payload: OrderPayload, db: Session = Depends(get_db)):
    """
    Execute a batch of orders for multiple clients.
    """
    responses = []

    # Fetch token_id for the given token_symbol and token_exchange
    token = db.query(TokenModel).filter(
        and_(TokenModel.symbol == order_payload.token_symbol, TokenModel.exchange == order_payload.token_exchange)
    ).first()

    if not token:
        # If token doesn't exist, create it. In a real scenario, you might want more robust token management.
        new_token = TokenModel(symbol=order_payload.token_symbol, exchange=order_payload.token_exchange, description="")
        db.add(new_token)
        db.commit()
        db.refresh(new_token)
        token = new_token

    for client_order in order_payload.client_orders:
        client = db.query(ClientModel).filter(ClientModel.id == client_order.client_id).first()
        if not client:
            responses.append(OrderResponse(
                mofsl_order_id="N/A",
                client_id=client_order.client_id,
                status="ERROR",
                message="Client not found"
            ))
            continue

        try:
            decrypted_api_key = decrypt(client.api_key_encrypted)
            decrypted_api_secret = decrypt(client.api_secret_encrypted)

            temp_password = "SOME_SECURE_PASSWORD"
            temp_2fa = "SOME_2FA_VALUE"

            mofsl_service = MofslApiService(
                api_key=decrypted_api_key,
                api_secret=decrypted_api_secret,
                client_id=client.client_id,
                password=temp_password,
                two_fa=temp_2fa,
            )

            # Placeholder for actual order placement details
            order_details = {
                "symbol": order_payload.token_symbol,
                "exchange": order_payload.token_exchange,
                "quantity": client_order.quantity,
                "type": order_payload.order_type,
                "side": order_payload.buy_or_sell,
                "producttype": order_payload.trade_type,
                # Add other necessary fields for MOFSL API place order
            }
            mofsl_response = mofsl_service.place_order(order_details)

            order_status = mofsl_response.get("status", "ERROR")
            mofsl_order_id = mofsl_response.get("data", {}).get("orderid", "N/A")
            message = mofsl_response.get("message", "Order placement failed")

            # Create a new Trade record if it's a BUY order and no open trade exists for this token/client
            # Or update existing trade for SELL orders
            trade = db.query(TradeModel).filter(
                and_(
                    TradeModel.client_id == client.id,
                    TradeModel.token_id == token.id,
                    TradeModel.status == TradeStatus.open
                )
            ).first()

            if order_payload.buy_or_sell == "BUY":
                if not trade:
                    trade = TradeModel(
                        client_id=client.id,
                        token_id=token.id,
                        quantity=client_order.quantity,
                        avg_entry_price=0.0, # This should be updated with actual execution price
                        status=TradeStatus.open
                    )
                    db.add(trade)
                else:
                    # For simplicity, just updating quantity. Real logic would average price.
                    trade.quantity += client_order.quantity
                db.commit()
                db.refresh(trade)

            # Record execution
            execution_type = ExecutionType.buy if order_payload.buy_or_sell == "BUY" else ExecutionType.sell
            new_execution = ExecutionModel(
                trade_id=trade.id if trade else None, # Associate with trade if exists
                mofsl_order_id=mofsl_order_id,
                type=execution_type,
                quantity=client_order.quantity,
                price=0.0, # This should be updated with actual execution price
            )
            db.add(new_execution)
            db.commit()
            db.refresh(new_execution)
            if trade: db.refresh(trade)

            responses.append(OrderResponse(
                mofsl_order_id=mofsl_order_id,
                client_id=client_order.client_id,
                status=order_status,
                message=message
            ))

        except HTTPException as e:
            responses.append(OrderResponse(
                mofsl_order_id="N/A",
                client_id=client_order.client_id,
                status="ERROR",
                message=f"API Error: {e.detail}"
            ))
        except Exception as e:
            responses.append(OrderResponse(
                mofsl_order_id="N/A",
                client_id=client_order.client_id,
                status="ERROR",
                message=f"An unexpected error occurred: {e}"
            ))
    return responses

@router.post("/exit-token", response_model=List[OrderResponse], status_code=status.HTTP_200_OK)
async def exit_token_for_clients(exit_payload: TokenExitPayload, db: Session = Depends(get_db)):
    """
    Handle bulk exiting a position in a specific token across multiple clients.
    """
    responses = []

    token = db.query(TokenModel).filter(
        and_(TokenModel.symbol == exit_payload.token_symbol, TokenModel.exchange == exit_payload.token_exchange)
    ).first()

    if not token:
        raise HTTPException(status_code=404, detail=f"Token {exit_payload.token_symbol} on {exit_payload.token_exchange} not found in system.")

    for client_id in exit_payload.clients_to_exit:
        client = db.query(ClientModel).filter(ClientModel.id == client_id).first()
        if not client:
            responses.append(OrderResponse(
                mofsl_order_id="N/A",
                client_id=client_id,
                status="ERROR",
                message="Client not found"
            ))
            continue

        try:
            decrypted_api_key = decrypt(client.api_key_encrypted)
            decrypted_api_secret = decrypt(client.api_secret_encrypted)

            temp_password = "SOME_SECURE_PASSWORD"
            temp_2fa = "SOME_2FA_VALUE"

            mofsl_service = MofslApiService(
                api_key=decrypted_api_key,
                api_secret=decrypted_api_secret,
                client_id=client.client_id,
                password=temp_password,
                two_fa=temp_2fa,
            )

            # 1. Get client's current positions to find the quantity of the token
            all_positions = mofsl_service.get_positions()
            position_found = False
            quantity_to_exit = 0
            current_ltp = 0.0

            if all_positions and isinstance(all_positions, dict) and "data" in all_positions:
                for position in all_positions["data"]:
                    if position.get("symbol") == exit_payload.token_symbol:
                        buy_quantity = position.get("buyquantity", 0)
                        sell_quantity = position.get("sellquantity", 0)
                        net_quantity = buy_quantity - sell_quantity

                        if net_quantity != 0: # Only consider open positions
                            quantity_to_exit = abs(net_quantity) # Exit the absolute net quantity
                            current_ltp = position.get("LTP", 0.0)
                            position_found = True
                            break
            
            if not position_found or quantity_to_exit == 0:
                responses.append(OrderResponse(
                    mofsl_order_id="N/A",
                    client_id=client_id,
                    status="SKIPPED",
                    message=f"No open position found for {exit_payload.token_symbol} for client {client.client_id}"
                ))
                continue

            # 2. Construct and place the SELL order
            order_details = {
                "symbol": exit_payload.token_symbol,
                "exchange": exit_payload.token_exchange,
                "quantity": quantity_to_exit,
                "type": "MARKET", # Always market order for exit
                "side": "SELL",
                "producttype": "INTRADAY", # Assuming intraday for exits, adjust if needed
                # Add other necessary fields for MOFSL API place order
            }
            mofsl_response = mofsl_service.place_order(order_details)

            order_status = mofsl_response.get("status", "ERROR")
            mofsl_order_id = mofsl_response.get("data", {}).get("orderid", "N/A")
            message = mofsl_response.get("message", "Order placement failed")

            # 3. Update Trade status and record Execution in DB
            trade = db.query(TradeModel).filter(
                and_(
                    TradeModel.client_id == client.id,
                    TradeModel.token_id == token.id,
                    TradeModel.status == TradeStatus.open
                )
            ).first()

            if trade:
                trade.status = TradeStatus.closed
                trade.exit_price = current_ltp # Use current LTP as exit price
                trade.exit_timestamp = datetime.now()
                db.add(trade)

            new_execution = ExecutionModel(
                trade_id=trade.id if trade else None, # Associate with trade if exists
                mofsl_order_id=mofsl_order_id,
                type=ExecutionType.sell,
                quantity=quantity_to_exit,
                price=current_ltp, # Use current LTP as execution price
            )
            db.add(new_execution)
            db.commit()
            db.refresh(new_execution)
            if trade: db.refresh(trade)

            responses.append(OrderResponse(
                mofsl_order_id=mofsl_order_id,
                client_id=client_id,
                status=order_status,
                message=message
            ))

        except HTTPException as e:
            responses.append(OrderResponse(
                mofsl_order_id="N/A",
                client_id=client_id,
                status="ERROR",
                message=f"API Error: {e.detail}"
            ))
        except Exception as e:
            responses.append(OrderResponse(
                mofsl_order_id="N/A",
                client_id=client_id,
                status="ERROR",
                message=f"An unexpected error occurred: {e}"
            ))

    return responses
