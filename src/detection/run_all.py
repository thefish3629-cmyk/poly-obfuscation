from ..data.api_clients import PolymarketClient
from ..data.subgraph_client import GoldskyClient
from ..data.onchain_client import OnchainClient
from ..storage.postgres_store import PostgresStore
from ..storage.graph_store import GraphStore
from ..detection.mixers import MixerDetector
from ..detection.bridges import BridgeDetector
from ..detection.sybil import SybilDetector
from ..detection.layering import LayeringDetector
from ..analysis.risk_scorer import RiskScorer
from ..analysis.reporter import Reporter
from ..models.database import init_db
from ..models.schemas import DetectionFlag
from ..utils.logging import setup_logging
from datetime import datetime
import random

logger = setup_logging("detection_runner")


class DetectionRunner:
    def __init__(self, test_mode: bool = False):
        self.store = PostgresStore()
        self.graph_store = GraphStore()
        self.test_mode = test_mode
        self.onchain = None
        
        if not test_mode:
            self.onchain = OnchainClient()
            self.mixer_detector = MixerDetector(self.store, self.onchain)
            self.bridge_detector = BridgeDetector(self.store, self.onchain)
            self.layering_detector = LayeringDetector(self.store, self.onchain)
        
        self.sybil_detector = SybilDetector(self.store)
        self.risk_scorer = RiskScorer(self.store)
        self.reporter = Reporter(self.store, self.graph_store)
    
    def run_all(self, addresses: list = None, market_id: str = None):
        """Run all detection modules."""
        logger.info("Starting detection pipeline...")
        
        if addresses is None:
            top_wallets = self.store.get_top_wallets_by_volume(limit=50, market_id=market_id)
            addresses = [w.address for w in top_wallets]
        
        logger.info(f"Running detection on {len(addresses)} wallets...")
        
        if self.test_mode:
            return self._run_test_detection(addresses, market_id)
        
        mixer_flags = self.mixer_detector.run_detection(addresses)
        logger.info(f"Mixer detection: {mixer_flags} flags")
        
        bridge_flags = self.bridge_detector.run_detection(addresses)
        logger.info(f"Bridge detection: {bridge_flags} flags")
        
        sybil_clusters = self.sybil_detector.run_detection(market_id)
        sybil_count = 0
        if sybil_clusters:
            sybil_count = self.sybil_detector.flag_cluster_members(sybil_clusters)
            logger.info(f"Sybil detection: {sybil_count} cluster memberships")
        
        layering_flags = self.layering_detector.run_detection(addresses)
        logger.info(f"Layering detection: {layering_flags} flags")
        
        logger.info("Calculating risk scores...")
        scores = self.risk_scorer.calculate_all_scores()
        
        logger.info("\nDetection Summary:")
        logger.info(f"  Wallets analyzed: {len(addresses)}")
        logger.info(f"  Mixer flags: {mixer_flags}")
        logger.info(f"  Bridge flags: {bridge_flags}")
        logger.info(f"  Sybil clusters: {len(sybil_clusters) if sybil_clusters else 0}")
        logger.info(f"  Layering flags: {layering_flags}")
        
        return {
            "mixer_flags": mixer_flags,
            "bridge_flags": bridge_flags,
            "sybil_clusters": len(sybil_clusters) if sybil_clusters else 0,
            "layering_flags": layering_flags,
            "scores": scores
        }
    
    def _run_test_detection(self, addresses: list, market_id: str):
        """Run simulated detection for testing."""
        logger.info("Running TEST detection (simulated flags)...")
        
        flag_types = ["mixer_indirect", "bridge_direct", "sybil_cluster", "layering_fan_pattern"]
        total_flags = 0
        
        for address in addresses:
            num_flags = random.randint(0, 2)
            for _ in range(num_flags):
                flag_type = random.choice(flag_types)
                confidence = random.randint(60, 95)
                
                flag = DetectionFlag(
                    wallet_address=address,
                    flag_type=flag_type,
                    confidence=float(confidence),
                    evidence={"test_mode": True},
                    detected_at=datetime.now()
                )
                self.store.add_detection_flag(flag)
                total_flags += 1
        
        sybil_clusters = self.sybil_detector.run_detection(market_id)
        sybil_count = 0
        if sybil_clusters:
            sybil_count = self.sybil_detector.flag_cluster_members(sybil_clusters)
        
        scores = self.risk_scorer.calculate_all_scores()
        
        logger.info(f"\nTest Detection Summary:")
        logger.info(f"  Wallets analyzed: {len(addresses)}")
        logger.info(f"  Simulated flags: {total_flags}")
        logger.info(f"  Sybil clusters: {len(sybil_clusters) if sybil_clusters else 0}")
        
        return {
            "mixer_flags": total_flags // 3,
            "bridge_flags": total_flags // 3,
            "sybil_clusters": len(sybil_clusters) if sybil_clusters else 0,
            "layering_flags": total_flags // 3,
            "scores": scores
        }
    
    def generate_report(self):
        """Generate and export detection report."""
        logger.info("Generating report...")
        
        self.reporter.export_to_json()
        self.reporter.export_to_csv()
        self.reporter.print_summary()


def main():
    from argparse import ArgumentParser
    
    parser = ArgumentParser(description="Run obfuscation detection")
    parser.add_argument("--market-id", type=str, help="Market condition ID")
    parser.add_argument("--limit", type=int, default=50, help="Number of top wallets to analyze")
    parser.add_argument("--test", action="store_true", help="Run with simulated detection")
    args = parser.parse_args()
    
    init_db()
    
    runner = DetectionRunner(test_mode=args.test)
    runner.run_all(market_id=args.market_id)
    runner.generate_report()


if __name__ == "__main__":
    main()
