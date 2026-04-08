"""Simple report without Sybil detection"""
from src.storage.postgres_store import PostgresStore
from src.analysis.risk_scorer import RiskScorer
from src.analysis.reporter import Reporter

print("=" * 60)
print("OBFUSCATION DETECTION REPORT")
print("=" * 60)

store = PostgresStore()
scorer = RiskScorer(store)
scores = scorer.calculate_all_scores()

# Get risk distribution
dist = scorer.get_risk_distribution()
flagged = scorer.get_flagged_wallets(min_score=0)

print(f"\nTotal Wallets: {dist['total_wallets']}")
print(f"With Flags: {len(flagged)}")

print("\nRisk Distribution:")
print(f"  Low (<25):     {dist['low_risk']['count']} ({dist['low_risk']['percentage']:.1f}%)")
print(f"  Medium (25-50): {dist['medium_risk']['count']} ({dist['medium_risk']['percentage']:.1f}%)")
print(f"  High (50-75):  {dist['high_risk']['count']} ({dist['high_risk']['percentage']:.1f}%)")
print(f"  Critical (>75): {dist['critical_risk']['count']} ({dist['critical_risk']['percentage']:.1f}%)")

print("\nTop 10 Riskiest Wallets:")
for i, w in enumerate(flagged[:10], 1):
    flags = [f['type'] for f in w.get('flags', [])]
    print(f"  {i}. {w['address'][:20]}... Score: {w['risk_score']:.1f} Flags: {flags}")

# Export CSV
reporter = Reporter(store)
reporter.export_to_csv()
print("\nCSV exported to reports/")
