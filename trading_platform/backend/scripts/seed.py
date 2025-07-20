# IMPORTANT: Before running this script, please ensure:
# 1. The `CSV_PATH` variable points to the correct location of your instruments CSV file.
# 2. The `symbol_column`, `exchange_column`, and `description_column` variables
#    accurately reflect the column headers in your CSV file that correspond to
#    the token symbol, exchange name, and token description, respectively.

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import and_
import os
import sys

# Add the parent directory to the Python path to allow imports from `app`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from trading_platform.backend.app.db.session import SessionLocal
from trading_platform.backend.app.models.token import Token as TokenModel

# --- Configuration ---
# Path to your instruments CSV file
CSV_PATH = './instruments (1).csv' # Update this path!

# Column names in your CSV file
symbol_column = 'scripshortname'    # Confirm this matches your CSV
exchange_column = 'exchangename'    # Confirm this matches your CSV
description_column = 'scripname'    # Confirm this matches your CSV
# --- End Configuration ---

def seed_tokens_from_csv():
    print(f"Attempting to seed tokens from: {CSV_PATH}")

    if not os.path.exists(CSV_PATH):
        print(f"Error: CSV file not found at {CSV_PATH}")
        print("Please update the CSV_PATH variable in backend/scripts/seed.py to the correct location.")
        return

    try:
        df = pd.read_csv(CSV_PATH)
        print(f"Successfully loaded CSV with {len(df)} rows.")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    db: Session = SessionLocal()
    added_count = 0

    try:
        # Fetch existing tokens for idempotency check
        existing_tokens = set()
        for token in db.query(TokenModel).all():
            existing_tokens.add((token.symbol, token.exchange))
        print(f"Found {len(existing_tokens)} existing tokens in the database.")

        for index, row in df.iterrows():
            symbol = str(row[symbol_column]).strip()
            exchange = str(row[exchange_column]).strip()
            description = str(row[description_column]).strip() if description_column in row and pd.notna(row[description_column]) else ""

            # Check if the token already exists to ensure idempotency
            if (symbol, exchange) not in existing_tokens:
                new_token = TokenModel(
                    symbol=symbol,
                    exchange=exchange,
                    description=description
                )
                db.add(new_token)
                added_count += 1
                existing_tokens.add((symbol, exchange)) # Add to set to prevent duplicates within the same run
            # else:
            #     print(f"Skipping duplicate: {symbol} on {exchange}")

        db.commit()
        print(f"Successfully added {added_count} new tokens to the database.")

    except KeyError as e:
        print(f"Error: Missing expected column in CSV. Please check `symbol_column`, `exchange_column`, and `description_column` variables. Missing: {e}")
        db.rollback()
    except Exception as e:
        print(f"An unexpected error occurred during database seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_tokens_from_csv()
