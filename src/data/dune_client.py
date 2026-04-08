import requests
from typing import List, Dict, Optional
from datetime import datetime
from ..models.schemas import Trade as TradeSchema
from ..utils.logging import setup_logging

logger = setup_logging("dune_client")


class DuneClient:
    BASE_URL = "https://api.dune.com/api/v1"
    
    # Default query for Iran-related Polymarket trades
    DEFAULT_IRAN_QUERY_ID = 6964724
    
    def __init__(self, api_key: str, query_id: int = None):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"x-dune-api-key": api_key})
    
    def execute_query(self, query_id: int, parameters: Dict = None) -> Dict:
        """Execute a saved Dune query."""
        url = f"{self.BASE_URL}/query/{query_id}/execute"
        payload = {"parameters": parameters} if parameters else {}
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_execution_status(self, execution_id: str) -> Dict:
        """Check status of query execution."""
        url = f"{self.BASE_URL}/execution/{execution_id}/status"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_execution_results(self, execution_id: str, limit: int = 10000) -> Dict:
        """Get results of completed execution."""
        url = f"{self.BASE_URL}/execution/{execution_id}/results"
        response = self.session.get(url, params={"limit": limit})
        response.raise_for_status()
        return response.json()
    
    def run_query_and_wait(self, query_id: int, timeout: int = 300) -> List[Dict]:
        """Run query and wait for results."""
        exec_data = self.execute_query(query_id)
        execution_id = exec_data["execution_id"]
        
        import time
        start = time.time()
        while time.time() - start < timeout:
            status = self.get_execution_status(execution_id)
            state = status["state"]
            
            if state == "QUERY_STATE_COMPLETED":
                results = self.get_execution_results(execution_id)
                return results.get("result", {}).get("rows", [])
            elif state == "QUERY_STATE_FAILED":
                raise Exception(f"Query failed: {status}")
            
            time.sleep(2)
        
        raise TimeoutError("Query timed out")
    
    def get_polymarket_trades(self, days: int = 30, limit: int = 10000) -> List[TradeSchema]:
        """Get Polymarket trades using Dune's saved query (query_id: 6964724)."""
        query_id = self.DEFAULT_IRAN_QUERY_ID
        
        url = f"{self.BASE_URL}/query/{query_id}/execute"
        payload = {
            "parameters": [
                {"name": "limit", "type": "number", "value": limit}
            ]
        }
        
        response = self.session.post(url, json=payload)
        if response.status_code == 200:
            exec_id = response.json()["execution_id"]
            logger.info(f"Started Dune query, execution_id: {exec_id}")
            
            import time
            start = time.time()
            while time.time() - start < 300:
                status = self.get_execution_status(exec_id)
                if status["state"] == "QUERY_STATE_COMPLETED":
                    results = self.get_execution_results(exec_id)
                    rows = results.get("result", {}).get("rows", [])
                    
                    return [
                        TradeSchema(
                            tx_hash=row.get("tx_hash", ""),
                            block_number=row.get("block_number", 0),
                            timestamp=datetime.fromisoformat(
                                row.get("block_time", "").replace("Z", "+00:00")
                            ),
                            market_id=row.get("condition_id", ""),
                            wallet_address=row.get("trader", "").lower(),
                            side=row.get("side", "").upper(),
                            amount_usd=float(row.get("amount_usd", 0)),
                        )
                        for row in rows
                    ]
                time.sleep(3)
        
        return []
    
    def get_trades_for_market(self, condition_id: str, limit: int = 5000) -> List[Dict]:
        """Get all trades for a specific market."""
        query = """
        SELECT
            block_time,
            tx_hash,
            block_number,
            trader,
            side,
            amount_usd,
            condition_id,
            question
        FROM polymarket_polygon.market_trades
        WHERE condition_id = :condition_id
        ORDER BY block_time DESC
        LIMIT :limit
        """
        
        url = f"{self.BASE_URL}/query/2435483/execute"
        payload = {
            "query_description": "Polymarket market trades",
            "parameters": [
                {"name": "condition_id", "type": "text", "value": condition_id},
                {"name": "limit", "type": "number", "value": limit}
            ]
        }
        
        response = self.session.post(url, json=payload)
        if response.status_code == 200:
            exec_id = response.json()["execution_id"]
            
            import time
            start = time.time()
            while time.time() - start < 300:
                status = self.get_execution_status(exec_id)
                if status["state"] == "QUERY_STATE_COMPLETED":
                    results = self.get_execution_results(exec_id)
                    return results.get("result", {}).get("rows", [])
                time.sleep(3)
        
        return []
