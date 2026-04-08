from typing import List, Dict
from datetime import datetime
from pathlib import Path
import json
import csv
from ..storage.postgres_store import PostgresStore
from ..storage.graph_store import GraphStore
from .risk_scorer import RiskScorer
from ..utils.logging import setup_logging

logger = setup_logging("reporter")


class Reporter:
    """Generate reports for obfuscation detection results."""
    
    def __init__(self, store: PostgresStore, graph_store: GraphStore = None):
        self.store = store
        self.graph_store = graph_store
        self.risk_scorer = RiskScorer(store)
        self.reports_dir = Path(__file__).parent.parent.parent / "reports"
        self.reports_dir.mkdir(exist_ok=True)
    
    def generate_executive_summary(self) -> Dict:
        """Generate executive summary of all detection results."""
        from ..models.database import DetectionFlag, Wallet
        
        risk_dist = self.risk_scorer.get_risk_distribution()
        flagged_wallets = self.risk_scorer.get_flagged_wallets()
        
        try:
            total_wallets = self.store.session.query(Wallet).count()
            all_flags = self.store.session.query(DetectionFlag).all()
        except Exception:
            total_wallets = 0
            all_flags = []
        
        summary = {
            "generated_at": datetime.now().isoformat(),
            "target_market": "Israel strike on Iranian nuclear facility before July?",
            "total_wallets_analyzed": total_wallets,
            "flagged_wallets": len(flagged_wallets),
            "total_detection_flags": len(all_flags),
            "risk_distribution": risk_dist,
            "top_risks": flagged_wallets[:10],
            "recommendations": self._generate_recommendations(risk_dist, flagged_wallets)
        }
        
        return summary
    
    def _generate_recommendations(self, risk_dist: Dict, flagged: List[Dict]) -> List[str]:
        """Generate recommendations based on findings."""
        recommendations = []
        
        if risk_dist.get("critical_risk", {}).get("count", 0) > 0:
            recommendations.append(
                f"CRITICAL: {risk_dist['critical_risk']['count']} wallets show critical risk scores. "
                "Immediate investigation recommended."
            )
        
        if risk_dist.get("high_risk", {}).get("count", 0) > 5:
            recommendations.append(
                f"HIGH: {risk_dist['high_risk']['count']} wallets show high risk patterns. "
                "Manual review of top 10 recommended."
            )
        
        mixer_flags = [w for w in flagged if any(
            f["type"].startswith("mixer") for f in w.get("flags", [])
        )]
        if mixer_flags:
            recommendations.append(
                f"ALERT: {len(mixer_flags)} wallets show potential mixer/privacy tool usage. "
                "Fund origins may be obfuscated."
            )
        
        sybil_flags = [w for w in flagged if any(
            f["type"].startswith("sybil") for f in w.get("flags", [])
        )]
        if sybil_flags:
            recommendations.append(
                f"WARNING: {len(sybil_flags)} wallets may be part of Sybil clusters. "
                "Coordinated trading behavior detected."
            )
        
        if not recommendations:
            recommendations.append("No significant obfuscation patterns detected.")
        
        return recommendations
    
    def export_to_json(self, filename: str = None) -> str:
        """Export full report to JSON."""
        if filename is None:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        summary = self.generate_executive_summary()
        filepath = self.reports_dir / filename
        
        with open(filepath, "w") as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"Report exported to {filepath}")
        return str(filepath)
    
    def export_to_csv(self, filename: str = None) -> str:
        """Export flagged wallets to CSV."""
        if filename is None:
            filename = f"flagged_wallets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        flagged = self.risk_scorer.get_flagged_wallets(min_score=0)
        filepath = self.reports_dir / filename
        
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Address", "Risk Score", "Mixer Score", "Bridge Score", 
                "Sybil Score", "Layering Score", "Flags"
            ])
            
            for wallet in flagged:
                writer.writerow([
                    wallet["address"],
                    f"{wallet['risk_score']:.1f}",
                    f"{wallet.get('mixer_score', 0):.1f}",
                    f"{wallet.get('bridge_score', 0):.1f}",
                    f"{wallet.get('sybil_score', 0):.1f}",
                    f"{wallet.get('layering_score', 0):.1f}",
                    json.dumps(wallet.get("flags", []))
                ])
        
        logger.info(f"CSV exported to {filepath}")
        return str(filepath)
    
    def generate_wallet_report(self, address: str) -> Dict:
        """Generate detailed report for a specific wallet."""
        wallet = self.store.get_wallet(address)
        if not wallet:
            return {"error": "Wallet not found"}
        
        flags = self.store.get_detection_flags(address)
        trades = self.store.get_trades_by_wallet(address)
        fund_hops = self.store.get_fund_hops_by_address(address)
        
        return {
            "address": address,
            "total_trades": len(trades),
            "total_volume_usd": sum(t.amount_usd for t in trades),
            "risk_score": wallet.risk_score,
            "flags": [
                {
                    "type": f.flag_type,
                    "confidence": f.confidence,
                    "evidence": f.evidence,
                    "detected_at": f.detected_at.isoformat() if f.detected_at else None
                }
                for f in flags
            ],
            "funding_sources": [
                {
                    "from": h.from_address,
                    "to": h.to_address,
                    "type": h.contract_type,
                    "amount": h.amount
                }
                for h in fund_hops[:20]
            ]
        }
    
    def print_summary(self):
        """Print human-readable summary to console."""
        summary = self.generate_executive_summary()
        
        print("\n" + "=" * 60)
        print("POLYMARKET OBFUSCATION DETECTION REPORT")
        print("=" * 60)
        print(f"Generated: {summary['generated_at']}")
        print(f"Target: {summary['target_market']}")
        print()
        print(f"Wallets Analyzed: {summary['total_wallets_analyzed']}")
        print(f"Flagged Wallets: {summary['flagged_wallets']}")
        print()
        
        dist = summary['risk_distribution']
        print("Risk Distribution:")
        print(f"  Low Risk (<25):     {dist['low_risk']['count']:4d} ({dist['low_risk']['percentage']:5.1f}%)")
        print(f"  Medium Risk (25-50):{dist['medium_risk']['count']:4d} ({dist['medium_risk']['percentage']:5.1f}%)")
        print(f"  High Risk (50-75):  {dist['high_risk']['count']:4d} ({dist['high_risk']['percentage']:5.1f}%)")
        print(f"  Critical (>75):     {dist['critical_risk']['count']:4d} ({dist['critical_risk']['percentage']:5.1f}%)")
        print()
        
        print("Top 10 Highest Risk Wallets:")
        for i, wallet in enumerate(summary['top_risks'][:10], 1):
            print(f"  {i}. {wallet['address'][:20]}... Score: {wallet['risk_score']:.1f}")
        print()
        
        print("Recommendations:")
        for rec in summary['recommendations']:
            print(f"  - {rec}")
        
        print("=" * 60)
