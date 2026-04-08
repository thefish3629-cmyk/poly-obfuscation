from typing import List, Dict, Set, Tuple
from datetime import datetime
from collections import defaultdict
from ..models.schemas import DetectionFlag
from ..storage.postgres_store import PostgresStore
from ..data.onchain_client import OnchainClient
from ..utils.logging import setup_logging
import networkx as nx

logger = setup_logging("layering_detector")


class LayeringDetector:
    """Detect money laundering layering patterns in fund flows."""
    
    FAN_OUT_THRESHOLD = 5
    FAN_IN_THRESHOLD = 5
    HOP_THRESHOLD = 3
    CIRCULAR_THRESHOLD = 0.3
    
    def __init__(self, store: PostgresStore, onchain: OnchainClient):
        self.store = store
        self.onchain = onchain
        self.graph = nx.DiGraph()
    
    def detect_for_wallet(self, address: str) -> List[DetectionFlag]:
        """Detect layering patterns for a specific wallet."""
        flags = []
        
        hops = self.onchain.trace_fund_origin(address, max_hops=5)
        
        if not hops:
            return flags
        
        fan_analysis = self._analyze_fan_patterns(hops, address)
        if fan_analysis["detected"]:
            flags.append(DetectionFlag(
                wallet_address=address,
                flag_type="layering_fan_pattern",
                confidence=fan_analysis["confidence"],
                evidence=fan_analysis,
                detected_at=datetime.now()
            ))
        
        circular_analysis = self._detect_circular_flows(hops, address)
        if circular_analysis["detected"]:
            flags.append(DetectionFlag(
                wallet_address=address,
                flag_type="layering_circular",
                confidence=circular_analysis["confidence"],
                evidence=circular_analysis,
                detected_at=datetime.now()
            ))
        
        multi_hop_analysis = self._analyze_multi_hop_patterns(hops, address)
        if multi_hop_analysis["detected"]:
            flags.append(DetectionFlag(
                wallet_address=address,
                flag_type="layering_multi_hop",
                confidence=multi_hop_analysis["confidence"],
                evidence=multi_hop_analysis,
                detected_at=datetime.now()
            ))
        
        return flags
    
    def _analyze_fan_patterns(self, hops: List[Dict], target_address: str) -> Dict:
        """Detect fan-out and fan-in patterns indicating layering."""
        fan_out = defaultdict(list)
        fan_in = defaultdict(list)
        
        for hop in hops:
            if hop["to_address"].lower() == target_address.lower():
                fan_in[hop["from_address"]].append(hop)
            elif hop["from_address"].lower() == target_address.lower():
                fan_out[hop["to_address"]].append(hop)
        
        fan_out_count = len(fan_out)
        fan_in_count = len(fan_in)
        
        detected = fan_out_count >= self.FAN_OUT_THRESHOLD or fan_in_count >= self.FAN_IN_THRESHOLD
        
        if detected:
            total_fan_out = sum(len(v) for v in fan_out.values())
            total_fan_in = sum(len(v) for v in fan_in.values())
            
            return {
                "detected": True,
                "confidence": 70.0,
                "details": {
                    "fan_out_wallets": fan_out_count,
                    "fan_in_wallets": fan_in_count,
                    "fan_out_tx_count": total_fan_out,
                    "fan_in_tx_count": total_fan_in,
                    "fan_out_addresses": list(fan_out.keys())[:10],
                    "fan_in_addresses": list(fan_in.keys())[:10]
                }
            }
        
        return {"detected": False, "confidence": 0, "details": {}}
    
    def _detect_circular_flows(self, hops: List[Dict], target_address: str) -> Dict:
        """Detect circular fund flow patterns."""
        address_hops = defaultdict(list)
        for hop in hops:
            address_hops[hop["from_address"]].append(hop["to_address"])
        
        circular_paths = []
        
        for start_addr, destinations in address_hops.items():
            for dest in destinations:
                if dest in address_hops:
                    for second_dest in address_hops[dest]:
                        if second_dest == start_addr:
                            circular_paths.append({
                                "path": [start_addr, dest, second_dest],
                                "completes_cycle": True
                            })
        
        if circular_paths:
            return {
                "detected": True,
                "confidence": 80.0,
                "details": {
                    "circular_paths_found": len(circular_paths),
                    "paths": circular_paths[:5]
                }
            }
        
        return {"detected": False, "confidence": 0, "details": {}}
    
    def _analyze_multi_hop_patterns(self, hops: List[Dict], target_address: str) -> Dict:
        """Detect excessive hop counts indicating layering."""
        target_hops = [h for h in hops if h["to_address"].lower() == target_address.lower()]
        
        if not target_hops:
            return {"detected": False, "confidence": 0, "details": {}}
        
        max_hop = max(h["hop_number"] for h in target_hops)
        
        if max_hop >= self.HOP_THRESHOLD:
            hop_distribution = defaultdict(int)
            for h in target_hops:
                hop_distribution[h["hop_number"]] += 1
            
            return {
                "detected": True,
                "confidence": 65.0,
                "details": {
                    "max_hops": max_hop,
                    "hop_distribution": dict(hop_distribution),
                    "total_funding_sources": len(set(h["from_address"] for h in target_hops))
                }
            }
        
        return {"detected": False, "confidence": 0, "details": {}}
    
    def build_fund_flow_graph(self, addresses: List[str]) -> nx.DiGraph:
        """Build a directed graph of fund flows for visualization."""
        self.graph = nx.DiGraph()
        
        for address in addresses:
            hops = self.onchain.trace_fund_origin(address, max_hops=3)
            for hop in hops:
                self.graph.add_edge(
                    hop["from_address"],
                    hop["to_address"],
                    token=hop["token"],
                    amount=hop["amount"],
                    contract_type=hop.get("contract_type", "unknown")
                )
        
        return self.graph
    
    def find_reconsolidation_points(self, target_address: str) -> List[Dict]:
        """Find wallets that might be reconsolidating funds."""
        hops = self.onchain.trace_fund_origin(target_address, max_hops=5)
        
        recipient_counts = defaultdict(list)
        for hop in hops:
            recipient_counts[hop["to_address"]].append(hop)
        
        reconsolidation_points = []
        
        for address, receiving_hops in recipient_counts.items():
            if len(receiving_hops) >= 3:
                sources = set(h["from_address"] for h in receiving_hops)
                if len(sources) >= 3:
                    reconsolidation_points.append({
                        "address": address,
                        "incoming_count": len(receiving_hops),
                        "unique_sources": len(sources),
                        "total_amount": sum(float(h["amount"]) for h in receiving_hops)
                    })
        
        return reconsolidation_points
    
    def run_detection(self, addresses: List[str] = None) -> int:
        """Run layering detection on all wallets or specified addresses."""
        if addresses is None:
            wallets = self.store.get_all_wallets()
            addresses = [w.address for w in wallets]
        
        total_flags = 0
        for address in addresses:
            flags = self.detect_for_wallet(address)
            for flag in flags:
                self.store.add_detection_flag(flag)
                total_flags += 1
        
        logger.info(f"Layering detection complete. Found {total_flags} flags.")
        return total_flags
