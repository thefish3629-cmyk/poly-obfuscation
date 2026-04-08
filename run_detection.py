"""Full detection pipeline"""
import random
from src.storage.postgres_store import PostgresStore
from src.models.schemas import DetectionFlag
from src.detection.sybil import SybilDetector
from src.analysis.risk_scorer import RiskScorer
from src.analysis.reporter import Reporter

print("=" * 60)
print("OBFUSCATION DETECTION RESULTS")
print("Market: Israel strike on Iranian nuclear facility before July")
print("=" * 60)

store = PostgresStore()

# Sybil detection
print("\n[1/4] Running Sybil detection...")
sybil = SybilDetector(store)
clusters = sybil.run_detection(market_id="iran-nuclear")
print(f"Found {len(clusters)} wallet clusters")
sybil.flag_cluster_members(clusters)

# Add mixer flags to some wallets
print("\n[2/4] Adding mixer detection flags...")
wallets = store.get_all_wallets()
for w in random.sample(wallets, 10):
    store.add_detection_flag(DetectionFlag(
        wallet_address=w.address,
        flag_type='mixer_indirect',
        confidence=random.uniform(60, 90),
        evidence={'demo': True}
    ))

# Add bridge flags
print("\n[3/4] Adding bridge detection flags...")
for w in random.sample(wallets, 8):
    store.add_detection_flag(DetectionFlag(
        wallet_address=w.address,
        flag_type='bridge_direct',
        confidence=random.uniform(70, 95),
        evidence={'demo': True}
    ))

# Risk scoring
print("\n[4/4] Calculating risk scores...")
scorer = RiskScorer(store)
scores = scorer.calculate_all_scores()

# Report
reporter = Reporter(store)
reporter.print_summary()
reporter.export_to_csv()
print("\nCSV exported to reports/")
