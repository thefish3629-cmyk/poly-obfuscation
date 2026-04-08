"""Quick pipeline run"""
import random
import hashlib
from datetime import datetime, timedelta
from src.storage.postgres_store import PostgresStore
from src.models.database import init_db, Market
from src.models.schemas import Trade as TradeSchema, DetectionFlag as DetectionFlagSchema
from src.detection.sybil import SybilDetector
from src.analysis.risk_scorer import RiskScorer
from src.analysis.reporter import Reporter

print("=" * 60)
print("POLYMARKET OBFUSCATION DETECTION")
print("Market: Israel strike on Iranian nuclear facility")
print("=" * 60)

init_db()
store = PostgresStore()

MARKET_ID = "iran-nuclear-july-2025"

# Generate 100 wallets with realistic patterns
random.seed(42)
wallets = []
for i in range(100):
    wallets.append({
        'address': '0x' + hashlib.sha256(f'wallet_{i}'.encode()).hexdigest()[:40],
        'volume': random.uniform(500, 25000),
        'cluster': i // 8 if random.random() < 0.25 else None
    })

# Generate trades
trades = []
for w in wallets:
    for j in range(random.randint(3, 15)):
        trades.append(TradeSchema(
            tx_hash='0x' + hashlib.sha256(f'{w["address"]}_{j}'.encode()).hexdigest(),
            block_number=85000000 + len(trades),
            timestamp=datetime(2025, 4, 1) + timedelta(days=random.randint(0, 60)),
            market_id=MARKET_ID,
            wallet_address=w['address'].lower(),
            side=random.choice(['BUY', 'SELL']),
            amount_usd=random.uniform(50, 2000)
        ))

store.add_trades_bulk(trades)
for w in wallets:
    store.upsert_wallet(w['address'], total_volume_usd=w['volume'])

# Sybil detection
print("\nRunning Sybil detection...")
sybil = SybilDetector(store)
clusters = sybil.run_detection(market_id=MARKET_ID)
sybil.flag_cluster_members(clusters)
print(f"Found {len(clusters)} clusters")

# Add some mixer/bridge flags
print("Adding detection flags...")
for w in random.sample(wallets, 15):
    store.add_detection_flag(DetectionFlagSchema(
        wallet_address=w['address'],
        flag_type='mixer_indirect',
        confidence=random.uniform(60, 90),
        evidence={'demo': True}
    ))
for w in random.sample(wallets, 10):
    store.add_detection_flag(DetectionFlagSchema(
        wallet_address=w['address'],
        flag_type='bridge_direct',
        confidence=random.uniform(70, 95),
        evidence={'demo': True}
    ))

# Risk scores
print("Calculating risk scores...")
scorer = RiskScorer(store)
scores = scorer.calculate_all_scores()

# Report
print("\n" + "=" * 60)
reporter = Reporter(store)
reporter.print_summary()

reporter.export_to_csv()
print("\nDone! CSV exported.")
