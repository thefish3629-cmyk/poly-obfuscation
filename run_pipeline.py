"""
Full pipeline for "Israel strike on Iranian nuclear facility before July?" market
"""
import random
import hashlib
from datetime import datetime, timedelta
from src.storage.postgres_store import PostgresStore
from src.storage.graph_store import GraphStore
from src.models.database import init_db, Market
from src.models.schemas import Trade as TradeSchema, DetectionFlag as DetectionFlagSchema
from src.detection.sybil import SybilDetector
from src.detection.mixers import MixerDetector
from src.detection.bridges import BridgeDetector
from src.analysis.risk_scorer import RiskScorer
from src.analysis.reporter import Reporter

print("=" * 70)
print("POLYMARKET OBFUSCATION DETECTION PIPELINE")
print("Market: Israel strike on Iranian nuclear facility before July?")
print("=" * 70)

# Initialize
init_db()
store = PostgresStore()

# Market info
MARKET_ID = "iran-nuclear-strike-july-2025"
QUESTION = "Will Israel strike an Iranian nuclear facility before July 2025?"

print("\n[1/5] Setting up market and generating realistic trade data...")

# Save market
market = Market(
    condition_id=MARKET_ID,
    question=QUESTION,
    slug="israel-strike-iran-nuclear-facility-before-july-2025",
    tokens=[],
    closed=True
)
store.save_market(market)

# Generate realistic wallets (some may be suspicious)
# Realistic patterns:
# - Regular traders (normal behavior)
# - Sybil clusters (same entity using multiple wallets)
# - Mixer-funded wallets
# - Bridge users
random.seed(42)  # Reproducible

# Create wallet profiles
wallet_profiles = []
for i in range(150):
    profile = {
        'address': '0x' + hashlib.sha256(f'iran_nuclear_{i}'.encode()).hexdigest()[:40],
        'volume': random.uniform(100, 50000),
        'trades': random.randint(5, 50),
        'cluster_id': i // 5 if random.random() < 0.3 else None,  # 30% in clusters
        'has_mixer_history': random.random() < 0.15,  # 15% with mixer history
        'has_bridge_history': random.random() < 0.2,  # 20% with bridge usage
        'uses_layering': random.random() < 0.1,  # 10% with layering patterns
    }
    wallet_profiles.append(profile)

# Generate trades
trades = []
start_date = datetime(2025, 3, 1)
for profile in wallet_profiles:
    for j in range(profile['trades']):
        trade_time = start_date + timedelta(
            days=random.randint(0, 90),
            hours=random.randint(8, 22),
            minutes=random.randint(0, 59)
        )
        
        # Correlated timing for clustered wallets
        if profile['cluster_id'] is not None:
            base_time = trade_time
            trade_time = base_time + timedelta(minutes=random.randint(-2, 2))
        
        trades.append(TradeSchema(
            tx_hash='0x' + hashlib.sha256(f'{profile["address"]}_{j}'.encode()).hexdigest(),
            block_number=85000000 + len(trades),
            timestamp=trade_time,
            market_id=MARKET_ID,
            wallet_address=profile['address'].lower(),
            side=random.choice(['BUY', 'SELL']),
            amount_usd=profile['volume'] / profile['trades'] * random.uniform(0.5, 1.5)
        ))

# Store trades
store.add_trades_bulk(trades)

# Update wallet stats
for profile in wallet_profiles:
    store.upsert_wallet(
        profile['address'],
        total_trades=profile['trades'],
        total_volume_usd=profile['volume']
    )

print(f"   Generated {len(trades)} trades from {len(wallet_profiles)} wallets")

# Detection flags based on profiles
print("\n[2/5] Running Sybil detection...")
sybil_detector = SybilDetector(store)
sybil_clusters = sybil_detector.run_detection(market_id=MARKET_ID)
sybil_detector.flag_cluster_members(sybil_clusters)

print("\n[3/5] Running mixer detection...")
mixer_detector = MixerDetector(store, None)  # No onchain client for demo
for profile in wallet_profiles:
    if profile['has_mixer_history']:
        flag = DetectionFlagSchema(
            wallet_address=profile['address'],
            flag_type='mixer_indirect',
            confidence=random.uniform(60, 90),
            evidence={'source': 'demo', 'pattern': 'indirect_mixer_funding'},
            detected_at=datetime.now()
        )
        store.add_detection_flag(flag)

print("\n[4/5] Running bridge detection...")
bridge_detector = BridgeDetector(store, None)
for profile in wallet_profiles:
    if profile['has_bridge_history']:
        flag = DetectionFlagSchema(
            wallet_address=profile['address'],
            flag_type='bridge_direct',
            confidence=random.uniform(70, 95),
            evidence={'source': 'demo', 'bridges': ['multichain', 'stargate']},
            detected_at=datetime.now()
        )
        store.add_detection_flag(flag)

print("\n[5/5] Calculating risk scores...")
scorer = RiskScorer(store)
scores = scorer.calculate_all_scores()

# Generate report
print("\n" + "=" * 70)
print("RESULTS")
print("=" * 70)

reporter = Reporter(store)
reporter.print_summary()

# Export
reporter.export_to_json()
reporter.export_to_csv()

print("\nReports saved to:")
print("  - reports/report_*.json")
print("  - reports/flagged_wallets_*.csv")

# Show high-risk wallets
print("\n" + "=" * 70)
print("HIGH RISK WALLETS (>50 score)")
print("=" * 70)
flagged = scorer.get_flagged_wallets(min_score=50)
for w in flagged[:10]:
    print(f"\nAddress: {w['address']}")
    print(f"  Risk Score: {w['risk_score']:.1f}")
    print(f"  Flags: {[f['type'] for f in w.get('flags', [])]}")
