from .reporter import Reporter
from ..models.database import init_db
from ..storage.postgres_store import PostgresStore
from ..storage.graph_store import GraphStore
from ..utils.logging import setup_logging

logger = setup_logging("report")


def main():
    logger.info("Generating detection reports...")
    
    init_db()
    
    store = PostgresStore()
    graph_store = GraphStore()
    reporter = Reporter(store, graph_store)
    
    logger.info("\n" + "=" * 60)
    reporter.print_summary()
    
    json_path = reporter.export_to_json()
    logger.info(f"JSON report saved to: {json_path}")
    
    csv_path = reporter.export_to_csv()
    logger.info(f"CSV report saved to: {csv_path}")
    
    store.close()


if __name__ == "__main__":
    main()
