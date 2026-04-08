from typing import List, Dict, Set
from datetime import datetime
from ..models.schemas import DetectionFlag
from ..storage.postgres_store import PostgresStore
from ..data.onchain_client import OnchainClient, BRIDGE_CONTRACTS
from ..utils.logging import setup_logging

logger = setup_logging("bridge_detector")


class BridgeDetector:
    KNOWN_BRIDGES = BRIDGE_CONTRACTS
    
    CROSS_CHAIN_INDICATORS = {
        "multichain": ["anySwap", "Anyswap"],
        "stargate": ["Stargate", "STG"],
        "layerzero": ["LayerZero", "LZ"],
        "wormhole": ["Wormhole", "WH"],
        "hop": ["Hop", "HOP"],
    }
    
    def __init__(self, store: PostgresStore, onchain: OnchainClient):
        self.store = store
        self.onchain = onchain
    
    def detect_for_wallet(self, address: str) -> List[DetectionFlag]:
        """Detect bridge usage for a specific wallet."""
        flags = []
        
        direct_bridges = self._check_direct_bridge_interaction(address)
        for bridge_info in direct_bridges:
            flags.append(DetectionFlag(
                wallet_address=address,
                flag_type="bridge_direct",
                confidence=bridge_info["confidence"],
                evidence=bridge_info,
                detected_at=datetime.now()
            ))
        
        chain_hopping = self._analyze_chain_hopping(address)
        if chain_hopping["detected"]:
            flags.append(DetectionFlag(
                wallet_address=address,
                flag_type="chain_hopping",
                confidence=chain_hopping["confidence"],
                evidence=chain_hopping,
                detected_at=datetime.now()
            ))
        
        return flags
    
    def _check_direct_bridge_interaction(self, address: str) -> List[Dict]:
        """Check if wallet has directly interacted with bridge contracts."""
        flags = []
        transfers = self.onchain.get_usdc_transfers(address)
        
        for transfer in transfers["incoming"] + transfers["outgoing"]:
            contract_type = self.onchain.get_contract_type(transfer["from"])
            
            if contract_type.startswith("bridge:"):
                bridge_name = contract_type.replace("bridge:", "")
                flags.append({
                    "bridge_type": bridge_name,
                    "tx_hash": transfer["tx_hash"],
                    "amount": transfer["value"],
                    "direction": "received" if transfer["to"].lower() == address.lower() else "sent",
                    "confidence": 90.0
                })
        
        return flags
    
    def _analyze_chain_hopping(self, address: str) -> Dict:
        """Detect patterns of bridging between chains."""
        hops = self.onchain.trace_fund_origin(address, max_hops=2)
        
        bridge_interactions = [
            h for h in hops 
            if h.get("contract_type", "").startswith("bridge")
        ]
        
        if len(bridge_interactions) >= 2:
            return {
                "detected": True,
                "confidence": 75.0,
                "details": {
                    "bridge_interactions": len(bridge_interactions),
                    "bridges_used": list(set(h["contract_type"] for h in bridge_interactions)),
                    "total_amount": sum(float(h["amount"]) for h in bridge_interactions)
                }
            }
        
        return {"detected": False, "confidence": 0, "details": {}}
    
    def run_detection(self, addresses: List[str] = None) -> int:
        """Run bridge detection on all wallets or specified addresses."""
        if addresses is None:
            wallets = self.store.get_all_wallets()
            addresses = [w.address for w in wallets]
        
        total_flags = 0
        for address in addresses:
            flags = self.detect_for_wallet(address)
            for flag in flags:
                self.store.add_detection_flag(flag)
                total_flags += 1
                logger.info(f"Bridge detection for {address}: {flag.flag_type}")
        
        logger.info(f"Bridge detection complete. Found {total_flags} flags.")
        return total_flags


class BridgeActivityAnalyzer:
    """Analyze bridge activity patterns for suspicious behavior."""
    
    SUSPICIOUS_THRESHOLDS = {
        "multiple_bridges": 3,
        "rapid_bridging": 5,
        "large_amount_threshold": 50000,
    }
    
    @staticmethod
    def analyze_bridge_frequency(bridge_transactions: List[Dict]) -> Dict:
        """Check for suspicious bridging frequency."""
        if not bridge_transactions:
            return {"suspicious": False, "confidence": 0}
        
        unique_bridges = set()
        for tx in bridge_transactions:
            for bridge_type, addresses in BridgeDetector.KNOWN_BRIDGES.items():
                if tx.get("contract_address", "").lower() in [a.lower() for a in addresses]:
                    unique_bridges.add(bridge_type)
        
        is_suspicious = len(unique_bridges) >= BridgeActivityAnalyzer.SUSPICIOUS_THRESHOLDS["multiple_bridges"]
        
        return {
            "suspicious": is_suspicious,
            "unique_bridges_used": len(unique_bridges),
            "bridges": list(unique_bridges),
            "confidence": 70 if is_suspicious else 0
        }
    
    @staticmethod
    def analyze_bridge_amounts(bridge_transactions: List[Dict]) -> Dict:
        """Check for large or unusual bridge amounts."""
        if not bridge_transactions:
            return {"large_bridges_detected": False, "confidence": 0}
        
        amounts = [tx.get("amount", 0) for tx in bridge_transactions]
        large_amounts = [a for a in amounts if a > BridgeActivityAnalyzer.SUSPICIOUS_THRESHOLDS["large_amount_threshold"]]
        
        if large_amounts:
            return {
                "large_bridges_detected": True,
                "large_amount_count": len(large_amounts),
                "total_large_amount": sum(large_amounts),
                "confidence": 65
            }
        
        return {"large_bridges_detected": False, "confidence": 0}
    
    @staticmethod
    def detect_wash_bridging(bridge_transactions: List[Dict]) -> Dict:
        """Detect potential wash bridging (bridge-debridge patterns)."""
        if len(bridge_transactions) < 4:
            return {"wash_bridging_detected": False, "confidence": 0}
        
        sources = [tx.get("source_chain") for tx in bridge_transactions]
        destinations = [tx.get("dest_chain") for tx in bridge_transactions]
        
        chain_pairs = list(zip(sources, destinations))
        reverse_pairs = [(d, s) for s, d in chain_pairs]
        
        matching_reverses = sum(1 for pair in reverse_pairs if pair in chain_pairs)
        
        if matching_reverses >= 2:
            return {
                "wash_bridging_detected": True,
                "matching_reverse_count": matching_reverses,
                "confidence": 80
            }
        
        return {"wash_bridging_detected": False, "confidence": 0}
