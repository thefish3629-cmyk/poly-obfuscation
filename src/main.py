from src.models.database import init_db
from src.data.ingest import DataIngestionPipeline
from src.detection.run_all import DetectionRunner
from src.analysis.reporter import Reporter
from src.utils.logging import setup_logging

logger = setup_logging("main")


def main():
    logger.info("=" * 60)
    logger.info("POLYMARKET OBFUSCATION DETECTION PIPELINE")
    logger.info("=" * 60)
    
    logger.info("\n[1/4] Initializing database...")
    init_db()
    
    logger.info("\n[2/4] Ingesting market data...")
    pipeline = DataIngestionPipeline()
    market = pipeline.run()
    
    logger.info("\n[3/4] Running detection modules...")
    runner = DetectionRunner()
    results = runner.run_all(market_id=market.condition_id)
    
    logger.info("\n[4/4] Generating report...")
    runner.generate_report()
    
    logger.info("\n" + "=" * 60)
    logger.info("PIPELINE COMPLETE")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
