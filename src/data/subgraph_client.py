import requests
from typing import List, Dict, Optional
from datetime import datetime
from ..models.schemas import Trade as TradeSchema
from ..utils.logging import setup_logging

logger = setup_logging("goldsky_client")


class GoldskyClient:
    BASE_URL = "https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs"
    
    SUBGRAPHS = {
        "orderbook": "/orderbook-subgraph/0.0.1/gn",
        "positions": "/positions-subgraph/0.0.7/gn",
        "activity": "/activity-subgraph/0.0.4/gn",
        "pnl": "/pnl-subgraph/0.0.14/gn",
    }
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"x-api-key": api_key})
    
    def _query(self, subgraph: str, query: str, variables: Dict = None) -> Dict:
        """Execute GraphQL query."""
        url = f"{self.BASE_URL}{self.SUBGRAPHS[subgraph]}"
        response = self.session.post(
            url,
            json={"query": query, "variables": variables} if variables else {"query": query}
        )
        response.raise_for_status()
        data = response.json()
        if "errors" in data:
            logger.error(f"GraphQL errors: {data['errors']}")
        return data.get("data", {})
    
    def get_trades_for_market(self, condition_id: str, first: int = 1000, 
                              skip: int = 0) -> List[TradeSchema]:
        """Get all trades for a specific market condition."""
        query = """
        query GetTrades($conditionId: String!, $first: Int!, $skip: Int!) {
            orderFilleds(
                where: {conditionId: $conditionId}
                first: $first
                skip: $skip
                orderBy: timestamp
                orderDirection: desc
            ) {
                id
                transactionHash
                blockNumber
                timestamp
                maker
                taker
                makerAmountFilled
                takerAmountFilled
                makerFee
                takerFee
                conditionId
                makerAssetId
                takerAssetId
                is liquidation
            }
        }
        """
        
        trades = []
        total_fetched = 0
        
        while True:
            data = self._query("orderbook", query, {
                "conditionId": condition_id,
                "first": first,
                "skip": skip + total_fetched
            })
            
            batch = data.get("orderFilleds", [])
            if not batch:
                break
            
            for tx in batch:
                timestamp = datetime.fromtimestamp(int(tx["timestamp"]))
                
                if tx["maker"]:
                    trades.append(TradeSchema(
                        tx_hash=tx["transactionHash"],
                        block_number=int(tx["blockNumber"]),
                        timestamp=timestamp,
                        market_id=tx["conditionId"],
                        wallet_address=tx["maker"].lower(),
                        side="BUY",
                        amount_usd=float(tx["makerAmountFilled"]) / 1e6,
                        outcome_token_id=tx.get("makerAssetId"),
                        maker=tx.get("maker"),
                        taker=tx.get("taker")
                    ))
                
                if tx["taker"]:
                    trades.append(TradeSchema(
                        tx_hash=tx["transactionHash"],
                        block_number=int(tx["blockNumber"]),
                        timestamp=timestamp,
                        market_id=tx["conditionId"],
                        wallet_address=tx["taker"].lower(),
                        side="SELL",
                        amount_usd=float(tx["takerAmountFilled"]) / 1e6,
                        outcome_token_id=tx.get("takerAssetId"),
                        maker=tx.get("maker"),
                        taker=tx.get("taker")
                    ))
            
            total_fetched += len(batch)
            logger.info(f"Fetched {total_fetched} trades so far...")
            
            if len(batch) < first:
                break
        
        return trades
    
    def get_user_balances(self, user_address: str) -> List[Dict]:
        """Get token balances for a user."""
        query = """
        query GetBalances($user: String!) {
            userBalances(where: {user: $user}) {
                id
                balance
                netBalance
                condition {
                    id
                    questionId
                }
            }
        }
        """
        data = self._query("positions", query, {"user": user_address.lower()})
        return data.get("userBalances", [])
    
    def get_user_activity(self, user_address: str, first: int = 100) -> List[Dict]:
        """Get splits, merges, redemptions for a user."""
        query = """
        query GetActivity($user: String!, $first: Int!) {
            splits(
                where: {user: $user}
                first: $first
                orderBy: timestamp
                orderDirection: desc
            ) {
                id
                user
                collateralAmount
                timestamp
                transactionHash
            }
            merges(
                where: {user: $user}
                first: $first
                orderBy: timestamp
                orderDirection: desc
            ) {
                id
                user
                collateralAmount
                timestamp
                transactionHash
            }
            redemptions(
                where: {user: $user}
                first: $first
                orderBy: timestamp
                orderDirection: desc
            ) {
                id
                redeemer
                collateralAmount
                timestamp
                transactionHash
            }
        }
        """
        data = self._query("activity", query, {"user": user_address.lower(), "first": first})
        return data
    
    def get_market_conditions(self, condition_id: str) -> List[Dict]:
        """Get market condition details."""
        query = """
        query GetConditions($conditionId: String!) {
            marketConditions(where: {conditionId: $conditionId}) {
                id
                conditionId
                questionId
                openInterest
                question {
                    title
                }
            }
        }
        """
        data = self._query("pnl", query, {"conditionId": condition_id})
        return data.get("marketConditions", [])
