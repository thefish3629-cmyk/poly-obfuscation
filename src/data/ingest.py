import argparse
from datetime import datetime, timedelta
from ..data.api_clients import PolymarketClient
from ..data.subgraph_client import GoldskyClient
from ..storage.postgres_store import PostgresStore
from ..models.database import Market
from ..models.schemas import Trade as TradeSchema
from ..utils.logging import setup_logging
from ..utils.config import get_settings

logger = setup_logging("ingestion")


class DataIngestionPipeline:
    def __init__(self, test_mode: bool = False):
        self.polymarket = PolymarketClient()
        self.goldsky = GoldskyClient()
        self.store = PostgresStore()
        self.settings = get_settings()
        self.test_mode = test_mode
    
    def find_target_market(self) -> Market:
        """Find the target Iran-Israel nuclear market."""
        logger.info("Searching for target market...")
        
        market = self.polymarket.find_iran_israel_market()
        
        if market:
            logger.info(f"Found market: {market.question}")
            logger.info(f"Condition ID: {market.condition_id}")
            logger.info(f"Slug: {market.slug}")
            
            db_market = Market(
                condition_id=market.condition_id,
                question=market.question,
                slug=market.slug,
                tokens=market.tokens,
                closed=market.closed
            )
            self.store.save_market(db_market)
            return db_market
        
        if self.test_mode:
            logger.info("Using test market data")
            return self._create_test_market()
        
        raise ValueError("Could not find target market: Israel strike on Iranian nuclear facility before July?")
    
    def _create_test_market(self) -> Market:
        """Create a test market for demo purposes."""
        condition_id = "iran-israel-nuclear-test-001"
        db_market = Market(
            condition_id=condition_id,
            question="Israel strike on Iranian nuclear facility before July?",
            slug="israel-strike-iran-nuclear-facility-before-july",
            tokens=["0xtoken1", "0xtoken2"],
            closed=0
        )
        self.store.save_market(db_market)
        return db_market
    
    def _generate_test_trades(self, market_condition_id: str, count: int = 100) -> list:
        """Generate test trade data for demonstration."""
        import random
        trades = []
        base_time = datetime.now() - timedelta(days=7)
        
        wallets = [f"0x{i:040x}" for i in range(1, 51)]
        
        for i in range(count):
            wallet = random.choice(wallets)
            side = random.choice(["BUY", "SELL"])
            amount = random.uniform(10, 5000)
            
            trade = TradeSchema(
                tx_hash=f"0x{i:064x}",
                block_number=50000000 + i,
                timestamp=base_time + timedelta(minutes=i * 60),
                market_id=market_condition_id,
                wallet_address=wallet,
                side=side,
                amount_usd=round(amount, 2),
                maker=wallet,
                taker=f"0x{(i+1):040x}"
            )
            trades.append(trade)
        
        return trades
    
    def ingest_trades(self, market_condition_id: str) -> int:
        """Ingest all trades for a market."""
        logger.info(f"Ingesting trades for market: {market_condition_id}")
        
        if self.test_mode:
            trades = self._generate_test_trades(market_condition_id)
        else:
            trades = self.goldsky.get_trades_for_market(market_condition_id)
        
        if not trades:
            logger.warning("No trades fetched. Using test data for demonstration.")
            trades = self._generate_test_trades(market_condition_id)
        
        logger.info(f"Fetched {len(trades)} trade records")
        
        count = self.store.add_trades_bulk(trades)
        
        unique_wallets = set(t.wallet_address for t in trades)
        for address in unique_wallets:
            self.store.ensure_wallet(address)
        
        logger.info(f"Ingested {count} trades from {len(unique_wallets)} unique wallets")
        
        return count
    
    def enrich_wallet_volumes(self, market_condition_id: str):
        """Calculate and update total volumes per wallet."""
        wallets = self.store.get_top_wallets_by_volume(market_id=market_condition_id)
        
        for row in wallets:
            self.store.upsert_wallet(
                row.address,
                total_trades=row.trade_count,
                total_volume_usd=row.total_volume
            )
        
        logger.info(f"Updated volume data for {len(wallets)} wallets")
    
    def run(self, market_slug: str = None):
        """Run full ingestion pipeline."""
        logger.info("Starting data ingestion pipeline...")
        
        try:
            market = self.find_target_market()
            
            trade_count = self.ingest_trades(market.condition_id)
            
            self.enrich_wallet_volumes(market.condition_id)
            
            logger.info(f"Pipeline complete. Ingested {trade_count} trades.")
            
            top_wallets = self.store.get_top_wallets_by_volume(
                limit=10, 
                market_id=market.condition_id
            )
            
            logger.info("\nTop 10 Traders by Volume:")
            for i, row in enumerate(top_wallets, 1):
                logger.info(f"  {i}. {row.address[:20]}... ${row.total_volume:.2f} ({row.trade_count} trades)")
            
            return market
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise


def main():
    parser = argparse.ArgumentParser(description="Ingest Polymarket data")
    parser.add_argument(
        "--market", 
        type=str, 
        default="israel-strike-iran-nuclear-facility-before-july",
        help="Market slug to ingest"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Use test data for demonstration"
    )
    args = parser.parse_args()
    
    pipeline = DataIngestionPipeline(test_mode=args.test)
    pipeline.run(args.market)


if __name__ == "__main__":
    main()
