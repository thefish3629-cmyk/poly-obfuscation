"""
Paginated Polymarket client for handling large datasets.
"""

import requests
from typing import List, Dict, Optional, Iterator
from datetime import datetime
from ..models.schemas import Trade as TradeSchema
from ..utils.logging import setup_logging

logger = setup_logging("polymarket_paginated")


class PaginatedPolymarketClient:
    """
    Polymarket API client with pagination support.
    Handles fetching all data across multiple pages.
    """
    
    BASE_URLS = {
        "gamma": "https://gamma.polymarket.com",
        "clob": "https://clob.polymarket.com", 
        "data": "https://data-api.polymarket.com",
        "api": "https://api.polymarket.com"
    }
    
    def __init__(self, max_page_size: int = 100):
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json", 
            "Content-Type": "application/json"
        })
        self.max_page_size = max_page_size
    
    def _get(self, base: str, endpoint: str, params: Dict = None) -> Dict:
        """Make GET request with error handling."""
        url = f"{base}{endpoint}"
        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def get_trades_paginated(
        self, 
        market_id: str = None, 
        user_address: str = None,
        max_trades: int = None,
        max_pages: int = None
    ) -> Iterator[Dict]:
        """
        Fetch all trades with automatic pagination.
        
        Args:
            market_id: Filter by market condition ID
            user_address: Filter by wallet address
            max_trades: Stop after this many trades (None = all)
            max_pages: Stop after this many API calls (None = unlimited)
        
        Yields:
            Individual trade dicts
        """
        page = 0
        total_fetched = 0
        
        while True:
            # Build params
            params = {"limit": self.max_page_size}
            if market_id:
                params["market"] = market_id
            if user_address:
                params["user"] = user_address
            
            # Make request (try data-api first)
            try:
                data = self._get("data", "/trades", params)
            except Exception as e:
                logger.warning(f"data-api failed: {e}, trying fallback")
                try:
                    data = self._get("gamma", "/trades", params)
                except:
                    data = []
            
            if not data:
                break
            
            for trade in data:
                yield trade
                total_fetched += 1
                
                if max_trades and total_fetched >= max_trades:
                    return
            
            page += 1
            
            # Stop conditions
            if len(data) < self.max_page_size:
                break
            if max_pages and page >= max_pages:
                break
        
        logger.info(f"Fetched {total_fetched} trades across {page} pages")
    
    def get_all_trades_as_schema(
        self,
        market_id: str = None,
        user_address: str = None,
        max_trades: int = None
    ) -> List[TradeSchema]:
        """
        Fetch all trades and convert to TradeSchema objects.
        """
        trades = []
        
        for trade_data in self.get_trades_paginated(
            market_id=market_id,
            user_address=user_address,
            max_trades=max_trades
        ):
            try:
                trade = TradeSchema(
                    tx_hash=trade_data.get("txHash", ""),
                    block_number=int(trade_data.get("blockNumber", 0)),
                    timestamp=datetime.fromtimestamp(
                        int(trade_data.get("timestamp", 0))
                    ),
                    market_id=trade_data.get("market", ""),
                    wallet_address=trade_data.get("user", ""),
                    side=trade_data.get("side", ""),
                    amount_usd=float(trade_data.get("amount", 0)) / 100 if trade_data.get("amount") else 0.0,
                    outcome_token_id=trade_data.get("outcomeTokenId"),
                    maker=trade_data.get("maker"),
                    taker=trade_data.get("taker")
                )
                trades.append(trade)
            except Exception as e:
                logger.warning(f"Failed to parse trade: {e}")
                continue
        
        return trades
    
    def get_positions_paginated(
        self,
        user_address: str,
        max_pages: int = None
    ) -> Iterator[Dict]:
        """
        Fetch all positions for a user with pagination.
        """
        page = 0
        
        while True:
            params = {"user": user_address}
            
            try:
                data = self._get("data", "/positions", params)
            except:
                data = []
            
            if not data:
                break
            
            for pos in data:
                yield pos
            
            page += 1
            if max_pages and page >= max_pages:
                break
            if len(data) < self.max_page_size:
                break
    
    def get_activity_paginated(
        self,
        user_address: str,
        max_pages: int = None
    ) -> Iterator[Dict]:
        """
        Fetch all activity for a user (splits, merges, redemptions).
        """
        page = 0
        
        while True:
            params = {"user": user_address}
            
            try:
                data = self._get("data", "/activity", params)
            except:
                data = []
            
            if not data:
                break
            
            for activity in data:
                yield activity
            
            page += 1
            if max_pages and page >= max_pages:
                break
            if len(data) < self.max_page_size:
                break


# Convenience function for quick access
def get_all_market_trades(market_id: str, max_trades: int = None) -> List[TradeSchema]:
    """
    Quick helper to get all trades for a market.
    
    Example:
        trades = get_all_market_trades("0x123...", max_trades=1000)
    """
    client = PaginatedPolymarketClient()
    return client.get_all_trades_as_schema(market_id=market_id, max_trades=max_trades)


def get_user_trades(user_address: str, max_trades: int = None) -> List[TradeSchema]:
    """
    Quick helper to get all trades for a wallet.
    
    Example:
        trades = get_user_trades("0xabc...", max_trades=500)
    """
    client = PaginatedPolymarketClient()
    return client.get_all_trades_as_schema(user_address=user_address, max_trades=max_trades)