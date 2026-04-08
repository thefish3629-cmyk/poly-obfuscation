from typing import List, Dict
from ..models.schemas import RiskScore, DetectionFlag
from ..storage.postgres_store import PostgresStore
from ..utils.logging import setup_logging

logger = setup_logging("risk_scorer")


RISK_WEIGHTS = {
    "mixer_direct": 40.0,
    "mixer_indirect": 25.0,
    "bridge_direct": 15.0,
    "chain_hopping": 10.0,
    "sybil_cluster": 25.0,
    "layering_fan_pattern": 20.0,
    "layering_circular": 25.0,
    "layering_multi_hop": 15.0,
}


class RiskScorer:
    """Calculate aggregate risk scores for wallets based on detection flags."""
    
    def __init__(self, store: PostgresStore):
        self.store = store
    
    def calculate_wallet_score(self, address: str) -> RiskScore:
        """Calculate risk score for a single wallet."""
        flags = self.store.get_detection_flags(address)
        
        mixer_score = 0.0
        bridge_score = 0.0
        sybil_score = 0.0
        layering_score = 0.0
        
        for flag in flags:
            weight = RISK_WEIGHTS.get(flag.flag_type, 10.0)
            contribution = weight * (flag.confidence / 100.0)
            
            if flag.flag_type.startswith("mixer"):
                mixer_score = max(mixer_score, contribution)
            elif flag.flag_type.startswith("bridge") or flag.flag_type.startswith("chain"):
                bridge_score = max(bridge_score, contribution)
            elif flag.flag_type.startswith("sybil"):
                sybil_score = max(sybil_score, contribution)
            elif flag.flag_type.startswith("layering"):
                layering_score = max(layering_score, contribution)
        
        total_score = min(mixer_score + bridge_score + sybil_score + layering_score, 100.0)
        
        risk_score = RiskScore(
            wallet_address=address,
            total_score=total_score,
            mixer_score=mixer_score,
            bridge_score=bridge_score,
            sybil_score=sybil_score,
            layering_score=layering_score,
            details={
                "flag_count": len(flags),
                "flags": [
                    {"type": f.flag_type, "confidence": f.confidence}
                    for f in flags
                ]
            }
        )
        
        self.store.update_wallet_risk_score(address, total_score)
        
        return risk_score
    
    def calculate_all_scores(self) -> List[RiskScore]:
        """Calculate risk scores for all wallets."""
        wallets = self.store.get_all_wallets()
        scores = []
        
        for wallet in wallets:
            score = self.calculate_wallet_score(wallet.address)
            scores.append(score)
            
            if score.total_score > 0:
                logger.info(f"Wallet {wallet.address[:10]}... Risk: {score.total_score:.1f}")
        
        return sorted(scores, key=lambda x: x.total_score, reverse=True)
    
    def get_risk_distribution(self) -> Dict:
        """Get distribution of risk scores across wallets."""
        wallets = self.store.get_all_wallets()
        
        low_risk = sum(1 for w in wallets if w.risk_score < 25)
        medium_risk = sum(1 for w in wallets if 25 <= w.risk_score < 50)
        high_risk = sum(1 for w in wallets if 50 <= w.risk_score < 75)
        critical_risk = sum(1 for w in wallets if w.risk_score >= 75)
        
        return {
            "total_wallets": len(wallets),
            "low_risk": {"count": low_risk, "percentage": low_risk / len(wallets) * 100 if wallets else 0},
            "medium_risk": {"count": medium_risk, "percentage": medium_risk / len(wallets) * 100 if wallets else 0},
            "high_risk": {"count": high_risk, "percentage": high_risk / len(wallets) * 100 if wallets else 0},
            "critical_risk": {"count": critical_risk, "percentage": critical_risk / len(wallets) * 100 if wallets else 0},
        }
    
    def get_flagged_wallets(self, min_score: float = 25) -> List[Dict]:
        """Get wallets with risk scores above threshold."""
        wallets = self.store.get_all_wallets()
        flagged = []
        
        for wallet in wallets:
            if wallet.risk_score >= min_score:
                flags = self.store.get_detection_flags(wallet.address)
                flagged.append({
                    "address": wallet.address,
                    "risk_score": wallet.risk_score,
                    "flags": [
                        {"type": f.flag_type, "confidence": f.confidence}
                        for f in flags
                    ]
                })
        
        return sorted(flagged, key=lambda x: x["risk_score"], reverse=True)
