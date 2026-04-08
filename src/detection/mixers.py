from typing import List, Dict, Tuple
from datetime import datetime
from ..models.schemas import DetectionFlag
from ..storage.postgres_store import PostgresStore
from ..data.onchain_client import OnchainClient, MIXER_CONTRACTS, BRIDGE_CONTRACTS
from ..utils.logging import setup_logging
import networkx as nx

logger = setup_logging("mixer_detector")


class MixerDetector:
    KNOWN_MIXERS = MIXER_CONTRACTS
    
    DENOMINATION_PATTERNS = {
        "tornado_cash_eth": [0.1, 1, 10, 100],
        "tornado_cash_usdc": [100, 1000, 10000],
    }
    
    def __init__(self, store: PostgresStore, onchain: OnchainClient):
        self.store = store
        self.onchain = onchain
    
    def detect_for_wallet(self, address: str) -> List[DetectionFlag]:
        """Detect mixer usage for a specific wallet."""
        flags = []
        
        direct_interaction = self._check_direct_mixer_interaction(address)
        if direct_interaction:
            flags.append(DetectionFlag(
                wallet_address=address,
                flag_type="mixer_direct",
                confidence=95.0,
                evidence=direct_interaction,
                detected_at=datetime.now()
            ))
        
        funding_analysis = self._analyze_funding_sources(address)
        if funding_analysis["mixer_funding_detected"]:
            flags.append(DetectionFlag(
                wallet_address=address,
                flag_type="mixer_indirect",
                confidence=funding_analysis["confidence"],
                evidence=funding_analysis,
                detected_at=datetime.now()
            ))
        
        return flags
    
    def _check_direct_mixer_interaction(self, address: str) -> Dict:
        """Check if wallet has directly interacted with mixer contracts."""
        transfers = self.onchain.get_usdc_transfers(address)
        
        for transfer in transfers["incoming"] + transfers["outgoing"]:
            for mixer_type, addresses in self.KNOWN_MIXERS.items():
                if transfer["from"].lower() in [a.lower() for a in addresses] or \
                   transfer["to"].lower() in [a.lower() for a in addresses]:
                    return {
                        "mixer_type": mixer_type,
                        "tx_hash": transfer["tx_hash"],
                        "amount": transfer["value"],
                        "direction": "incoming" if transfer["to"].lower() == address.lower() else "outgoing"
                    }
        
        return None
    
    def _analyze_funding_sources(self, address: str) -> Dict:
        """Analyze funding patterns for mixer-like behavior."""
        hops = self.onchain.trace_fund_origin(address, max_hops=3)
        
        mixer_hops = [h for h in hops if h.get("contract_type", "").startswith("mixer")]
        
        if not mixer_hops:
            return {"mixer_funding_detected": False, "confidence": 0, "details": {}}
        
        analysis = {
            "mixer_funding_detected": True,
            "confidence": 70.0,
            "details": {
                "mixer_hops": len(mixer_hops),
                "total_hops": len(hops),
                "mixer_addresses": list(set(h["from_address"] for h in mixer_hops)),
                "estimated_funding_amount": sum(float(h["amount"]) for h in mixer_hops)
            }
        }
        
        if analysis["details"]["mixer_hops"] >= 2:
            analysis["confidence"] = 85.0
        
        return analysis
    
    def run_detection(self, addresses: List[str] = None) -> int:
        """Run mixer detection on all wallets or specified addresses."""
        if addresses is None:
            wallets = self.store.get_all_wallets()
            addresses = [w.address for w in wallets]
        
        total_flags = 0
        for address in addresses:
            flags = self.detect_for_wallet(address)
            for flag in flags:
                self.store.add_detection_flag(flag)
                total_flags += 1
                logger.info(f"Mixer detection for {address}: {flag.flag_type} ({flag.confidence}%)")
        
        logger.info(f"Mixer detection complete. Found {total_flags} flags.")
        return total_flags


class TornadoHeuristics:
    """Advanced heuristics for Tornado Cash detection."""
    
    FIFO_MATCH_THRESHOLD = 0.85
    GAS_PRICE_VARIANCE_THRESHOLD = 0.1
    
    @staticmethod
    def analyze_timing_patterns(transactions: List[Dict]) -> Dict:
        """Analyze transaction timing for Tornado-like patterns."""
        if len(transactions) < 2:
            return {"suspicious": False, "pattern": None, "confidence": 0}
        
        timestamps = [tx.get("timestamp") for tx in transactions if tx.get("timestamp")]
        if len(timestamps) < 2:
            return {"suspicious": False, "pattern": None, "confidence": 0}
        
        intervals = []
        for i in range(1, len(timestamps)):
            delta = (timestamps[i] - timestamps[i-1]).total_seconds()
            intervals.append(delta)
        
        avg_interval = sum(intervals) / len(intervals)
        variance = sum((i - avg_interval) ** 2 for i in intervals) / len(intervals)
        
        is_suspicious = variance < 10 and avg_interval < 60
        
        return {
            "suspicious": is_suspicious,
            "avg_interval_seconds": avg_interval,
            "variance": variance,
            "pattern": "regular_intervals" if is_suspicious else "random",
            "confidence": 60 if is_suspicious else 0
        }
    
    @staticmethod
    def analyze_denomination_patterns(amounts: List[float]) -> Dict:
        """Check for Tornado Cash denomination patterns."""
        tornado_denominations = {0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0}
        
        matches = [a for a in amounts if a in tornado_denominations]
        
        if len(matches) / len(amounts) > 0.5:
            return {
                "matches_tornado_denominations": True,
                "matched_amounts": matches,
                "confidence": 75.0
            }
        
        return {
            "matches_tornado_denominations": False,
            "matched_amounts": [],
            "confidence": 0
        }
    
    @staticmethod
    def analyze_gas_price_fingerprint(transactions: List[Dict]) -> Dict:
        """Check for common gas price signatures."""
        if not transactions:
            return {"suspicious": False, "confidence": 0}
        
        gas_prices = [tx.get("gas_price", 0) for tx in transactions if tx.get("gas_price")]
        if len(gas_prices) < 3:
            return {"suspicious": False, "confidence": 0}
        
        avg_gas = sum(gas_prices) / len(gas_prices)
        unique_prices = len(set(gas_prices))
        
        fingerprint_strength = 1 - (unique_prices / len(gas_prices))
        
        return {
            "suspicious": fingerprint_strength > 0.7,
            "fingerprint_strength": fingerprint_strength,
            "unique_gas_prices": unique_prices,
            "confidence": fingerprint_strength * 80
        }
