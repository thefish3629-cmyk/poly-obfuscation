"""Minimal pipeline - no Neo4j"""
import random
import hashlib
from datetime import datetime, timedelta
from src.storage.postgres_store import PostgresStore
from src.models.database import init_db
from src.models.schemas import Trade as TradeSchema, DetectionFlag as DetectionFlagSchema

print("Starting pipeline...")

# Initialize DB
init_db()
store = PostgresStore()

# Clear existing data
print("Clearing old data...")
try:
    store.session.query(type(store.session.query(DetectionFlagSchema).__class__)).delete()
except:
    pass

# Generate data
print("Generating trade data...")
random.seed(42)
trades = []
wallets = []

for i in range(80):
    addr = '0x' + hashlib.sha256(f'wallet_{i}'.encode()).hexdigest()[:40]
    wallets.append(addr)
    
    for j in range(random.randint(2, 12)):
        trades.append(TradeSchema(
            tx_hash='0x' + hashlib.sha256(f'{addr}_{j}'.encode()).hexdigest(),
            block_number=85000000 + len(trades),
            timestamp=datetime(2025, 4, 1) + timedelta(days=random.randint(0, 60)),
            market_id="iran-nuclear-july-2025",
            wallet_address=addr,
            side=random.choice(['BUY', 'SELL']),
            amount_usd=random.uniform(100, 3000)
        ))

print(f"Adding {len(trades)} trades...")
store.add_trades_bulk(trades)

for w in wallets[:30]:
    store.upsert_wallet(w, total_volume_usd=random.uniform(1000, 20000))

# Add flags
print("Adding detection flags...")
for w in random.sample(wallets, 12):
    store.add_detection_flag(DetectionFlagSchema(
        wallet_address=w,
        flag_type='sybil_cluster',
        confidence=random.uniform(65, 90),
        evidence={'demo': True}
    ))

for w in random.sample(wallets, 8):
    store.add_detection_flag(DetectionFlagSchema(
        wallet_address=w,
        flag_type='mixer_indirect',
        confidence=random.uniform(60, 85),
        evidence={'demo': True}
    ))

print("Calculating scores...")
from src.analysis.risk_scorer import RiskScorer
scorer = RiskScorer(store)
scores = scorer.calculate_all_scores()

print("\n" + "=" * 50)
print(f"Total wallets: {len(scores)}")
print(f"With flags: {len([s for s in scores if s.total_score > 0])}")

flagged = scorer.get_flagged_wallets(min_score=20)
print(f"High risk (>20): {len(flagged)}")

if flagged:
    print("\nTop 5 riskiest wallets:")
    for w in flagged[:5]:
        print(f"  {w['address'][:20]}... Score: {w['risk_score']:.1f}")

print("\nDone!")
