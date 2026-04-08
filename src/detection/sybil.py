from typing import List, Dict, Set, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
from ..models.schemas import DetectionFlag
from ..models.database import Trade
from ..storage.postgres_store import PostgresStore
from ..utils.logging import setup_logging
import networkx as nx

logger = setup_logging("sybil_detector")


class SybilDetector:
    """Detect Sybil attacks - multiple wallets controlled by the same entity."""
    
    def __init__(self, store: PostgresStore):
        self.store = store
        self.graph = nx.Graph()
    
    def detect_clusters(self, market_id: str = None) -> List[Dict]:
        """Detect wallet clusters using multiple heuristics."""
        trades = self.store.get_trades_by_market(market_id) if market_id else \
                 self.store.session.query(Trade).all()
        
        clusters = []
        
        timing_clusters = self._cluster_by_timing(trades)
        if timing_clusters:
            clusters.extend(timing_clusters)
        
        pattern_clusters = self._cluster_by_trading_pattern(trades)
        if pattern_clusters:
            clusters.extend(pattern_clusters)
        
        gas_clusters = self._cluster_by_gas_behavior(trades)
        if gas_clusters:
            clusters.extend(gas_clusters)
        
        coordinated_clusters = self._cluster_by_coordination(trades)
        if coordinated_clusters:
            clusters.extend(coordinated_clusters)
        
        merged_clusters = self._merge_clusters(clusters)
        
        return merged_clusters
    
    def _cluster_by_timing(self, trades: List[Trade]) -> List[Dict]:
        """Cluster wallets that execute trades at suspiciously similar times."""
        clusters = []
        
        wallet_times = defaultdict(list)
        for trade in trades:
            wallet_times[trade.wallet_address].append(trade.timestamp)
        
        addresses = list(wallet_times.keys())
        for i, addr1 in enumerate(addresses):
            for addr2 in addresses[i+1:]:
                times1 = sorted(wallet_times[addr1])
                times2 = sorted(wallet_times[addr2])
                
                sync_score = self._calculate_timing_similarity(times1, times2)
                
                if sync_score > 0.7:
                    clusters.append({
                        "type": "timing",
                        "wallets": [addr1, addr2],
                        "confidence": sync_score * 80,
                        "evidence": {
                            "addr1_trades": len(times1),
                            "addr2_trades": len(times2),
                            "sync_score": sync_score
                        }
                    })
        
        return clusters
    
    def _calculate_timing_similarity(self, times1: List[datetime], times2: List[datetime]) -> float:
        """Calculate how synchronized two sets of transaction times are."""
        if len(times1) < 2 or len(times2) < 2:
            return 0.0
        
        time_windows = []
        for t1 in times1:
            for t2 in times2:
                delta = abs((t1 - t2).total_seconds())
                if delta < 60:
                    time_windows.append(1)
                else:
                    time_windows.append(0)
        
        if not time_windows:
            return 0.0
        
        return sum(time_windows) / len(time_windows)
    
    def _cluster_by_trading_pattern(self, trades: List[Trade]) -> List[Dict]:
        """Cluster wallets with identical trading patterns."""
        wallet_patterns = defaultdict(lambda: {"sides": [], "markets": [], "volumes": []})
        
        for trade in trades:
            wallet_patterns[trade.wallet_address]["sides"].append(trade.side)
            wallet_patterns[trade.wallet_address]["markets"].append(trade.market_id)
            wallet_patterns[trade.wallet_address]["volumes"].append(trade.amount_usd)
        
        addresses = list(wallet_patterns.keys())
        clusters = []
        
        for i, addr1 in enumerate(addresses):
            for addr2 in addresses[i+1:]:
                pattern1 = wallet_patterns[addr1]
                pattern2 = wallet_patterns[addr2]
                
                similarity = self._pattern_similarity(pattern1, pattern2)
                
                if similarity > 0.8:
                    clusters.append({
                        "type": "pattern",
                        "wallets": [addr1, addr2],
                        "confidence": similarity * 85,
                        "evidence": {
                            "pattern1": pattern1,
                            "pattern2": pattern2,
                            "similarity": similarity
                        }
                    })
        
        return clusters
    
    def _pattern_similarity(self, pattern1: Dict, pattern2: Dict) -> float:
        """Calculate similarity between two trading patterns."""
        market_overlap = len(set(pattern1["markets"]) & set(pattern2["markets"]))
        if market_overlap == 0:
            return 0.0
        
        side_match = sum(1 for s1, s2 in zip(pattern1["sides"], pattern2["sides"]) if s1 == s2)
        side_similarity = side_match / max(len(pattern1["sides"]), len(pattern2["sides"]), 1)
        
        avg_vol1 = sum(pattern1["volumes"]) / len(pattern1["volumes"]) if pattern1["volumes"] else 0
        avg_vol2 = sum(pattern2["volumes"]) / len(pattern2["volumes"]) if pattern2["volumes"] else 0
        
        vol_ratio = min(avg_vol1, avg_vol2) / max(avg_vol1, avg_vol2) if max(avg_vol1, avg_vol2) > 0 else 0
        
        return (side_similarity + vol_ratio) / 2
    
    def _cluster_by_gas_behavior(self, trades: List[Trade]) -> List[Dict]:
        """Cluster wallets with similar gas price preferences."""
        return []
    
    def _cluster_by_coordination(self, trades: List[Trade]) -> List[Dict]:
        """Detect coordinated trading (same market, similar time, correlated positions)."""
        market_wallets = defaultdict(list)
        
        for trade in trades:
            market_wallets[trade.market_id].append({
                "address": trade.wallet_address,
                "side": trade.side,
                "timestamp": trade.timestamp,
                "volume": trade.amount_usd
            })
        
        clusters = []
        
        for market_id, wallet_trades in market_wallets.items():
            by_side = defaultdict(list)
            for wt in wallet_trades:
                by_side[wt["side"]].append(wt)
            
            for side, trades_list in by_side.items():
                if len(trades_list) >= 2:
                    sorted_trades = sorted(trades_list, key=lambda x: x["timestamp"])
                    
                    for i, t1 in enumerate(sorted_trades):
                        for t2 in sorted_trades[i+1:]:
                            time_diff = (t2["timestamp"] - t1["timestamp"]).total_seconds()
                            
                            if 0 < time_diff < 300:
                                vol_ratio = min(t1["volume"], t2["volume"]) / max(t1["volume"], t2["volume"]) if max(t1["volume"], t2["volume"]) > 0 else 0
                                
                                if vol_ratio > 0.8:
                                    clusters.append({
                                        "type": "coordinated",
                                        "wallets": [t1["address"], t2["address"]],
                                        "confidence": 75.0,
                                        "evidence": {
                                            "market_id": market_id,
                                            "side": side,
                                            "time_diff_seconds": time_diff,
                                            "vol_ratio": vol_ratio
                                        }
                                    })
        
        return clusters
    
    def _merge_clusters(self, clusters: List[Dict]) -> List[Dict]:
        """Merge overlapping clusters into larger groups using connected components."""
        if not clusters:
            return []
        
        G = nx.Graph()
        
        for cluster in clusters:
            wallets = cluster["wallets"]
            for w in wallets:
                if w not in G:
                    G.add_node(w, clusters=[], max_confidence=0)
                G.nodes[w]["clusters"].append(cluster["type"])
                G.nodes[w]["max_confidence"] = max(G.nodes[w]["max_confidence"], cluster["confidence"])
            
            for i, w1 in enumerate(wallets):
                for w2 in wallets[i+1:]:
                    G.add_edge(w1, w2)
        
        merged = []
        for component in nx.connected_components(G):
            if len(component) > 1:
                nodes = list(component)
                avg_confidence = sum(G.nodes[n]["max_confidence"] for n in nodes) / len(nodes)
                
                cluster_types = set()
                for n in nodes:
                    cluster_types.update(G.nodes[n]["clusters"])
                
                merged.append({
                    "type": "merged",
                    "wallets": nodes,
                    "confidence": avg_confidence,
                    "evidence": {
                        "original_count": len(nodes),
                        "cluster_types": list(cluster_types)
                    }
                })
        
        return merged
    
    def flag_cluster_members(self, clusters: List[Dict]) -> int:
        """Add detection flags for all wallets in detected clusters."""
        total_flags = 0
        
        for cluster in clusters:
            for wallet in cluster["wallets"]:
                flag = DetectionFlag(
                    wallet_address=wallet,
                    flag_type="sybil_cluster",
                    confidence=cluster["confidence"],
                    evidence=cluster,
                    detected_at=datetime.now()
                )
                self.store.add_detection_flag(flag)
                total_flags += 1
        
        logger.info(f"Sybil detection complete. Flagged {total_flags} wallet-cluster associations.")
        return total_flags
    
    def run_detection(self, market_id: str = None) -> List[Dict]:
        """Run full Sybil detection pipeline."""
        logger.info(f"Starting Sybil detection for market: {market_id or 'all'}")
        
        clusters = self.detect_clusters(market_id)
        
        logger.info(f"Found {len(clusters)} potential clusters")
        
        for cluster in clusters:
            logger.info(f"Cluster: {cluster['type']} - {cluster['wallets'][:3]}... "
                       f"(confidence: {cluster['confidence']:.1f}%)")
        
        return clusters
