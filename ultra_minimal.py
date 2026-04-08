"""Ultra minimal pipeline"""
import random
import hashlib
from datetime import datetime, timedelta

print("Connecting to database...")
from src.storage.postgres_store import PostgresStore
from src.models.database import init_db
from src.models.schemas import Trade as TradeSchema

init_db()
store = PostgresStore()
print("Connected!")

# Generate trades
print("Generating data...")
random.seed(42)
trades = []
for i in range(50):
    addr = '0x' + hashlib.sha256(f'wallet_{i}'.encode()).hexdigest()[:40]
    for j in range(random.randint(2, 8)):
        trades.append(TradeSchema(
            tx_hash='0x' + hashlib.sha256(f'{addr}_{j}'.encode()).hexdigest(),
            block_number=85000000,
            timestamp=datetime(2025, 4, 1),
            market_id="iran-nuclear",
            wallet_address=addr,
            side='BUY',
            amount_usd=random.uniform(100, 2000)
        ))

print(f"Inserting {len(trades)} trades...")
store.add_trades_bulk(trades)
print("Done!")
