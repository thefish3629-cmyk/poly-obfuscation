from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime
from ..models.database import Wallet, Trade, DetectionFlag, FundHop, Market, get_session
from ..models.schemas import Wallet as WalletSchema, Trade as TradeSchema, DetectionFlag as DetectionFlagSchema


class PostgresStore:
    def __init__(self):
        self.session: Session = get_session()
    
    def close(self):
        self.session.close()
    
    def ensure_wallet(self, address: str) -> Wallet:
        wallet = self.session.query(Wallet).filter(Wallet.address == address).first()
        if not wallet:
            wallet = Wallet(address=address, first_seen=datetime.now())
            self.session.add(wallet)
            self.session.commit()
        return wallet
    
    def upsert_wallet(self, address: str, **kwargs) -> Wallet:
        wallet = self.ensure_wallet(address)
        for key, value in kwargs.items():
            if hasattr(wallet, key):
                setattr(wallet, key, value)
        self.session.commit()
        return wallet
    
    def get_wallet(self, address: str) -> Optional[Wallet]:
        return self.session.query(Wallet).filter(Wallet.address == address).first()
    
    def get_all_wallets(self) -> List[Wallet]:
        return self.session.query(Wallet).all()
    
    def get_top_wallets_by_volume(self, limit: int = 20, market_id: Optional[str] = None) -> List[dict]:
        from sqlalchemy import func
        query = self.session.query(
            Wallet.address,
            func.sum(Trade.amount_usd).label("total_volume"),
            func.count(Trade.id).label("trade_count")
        ).join(Trade, Wallet.address == Trade.wallet_address)
        
        if market_id:
            query = query.filter(Trade.market_id == market_id)
        
        return query.group_by(Wallet.address)\
            .order_by(func.sum(Trade.amount_usd).desc())\
            .limit(limit)\
            .all()
    
    def add_trade(self, trade: TradeSchema) -> Trade:
        db_trade = Trade(**trade.model_dump(exclude={"id"}))
        self.session.add(db_trade)
        
        self.ensure_wallet(trade.wallet_address)
        self.session.commit()
        return db_trade
    
    def add_trades_bulk(self, trades: List[TradeSchema]) -> int:
        for trade in trades:
            db_trade = Trade(**trade.model_dump(exclude={"id"}))
            self.session.add(db_trade)
            self.ensure_wallet(trade.wallet_address)
        self.session.commit()
        return len(trades)
    
    def get_trades_by_wallet(self, address: str) -> List[Trade]:
        return self.session.query(Trade).filter(Trade.wallet_address == address).all()
    
    def get_trades_by_market(self, market_id: str) -> List[Trade]:
        return self.session.query(Trade).filter(Trade.market_id == market_id).all()
    
    def add_detection_flag(self, flag: DetectionFlagSchema) -> DetectionFlag:
        db_flag = DetectionFlag(**flag.model_dump())
        self.session.add(db_flag)
        
        wallet = self.get_wallet(flag.wallet_address)
        if wallet:
            flags = wallet.flags or {}
            flags[flag.flag_type] = flag.confidence
            wallet.flags = flags
        self.session.commit()
        return db_flag
    
    def get_detection_flags(self, address: str) -> List[DetectionFlag]:
        return self.session.query(DetectionFlag).filter(
            DetectionFlag.wallet_address == address
        ).all()
    
    def add_fund_hop(self, hop_data: dict) -> FundHop:
        hop = FundHop(**hop_data)
        self.session.add(hop)
        self.session.commit()
        return hop
    
    def add_fund_hops_bulk(self, hops: List[dict]) -> int:
        for hop_data in hops:
            hop = FundHop(**hop_data)
            self.session.add(hop)
        self.session.commit()
        return len(hops)
    
    def get_fund_hops(self, trace_id: str) -> List[FundHop]:
        return self.session.query(FundHop).filter(
            FundHop.trace_id == trace_id
        ).order_by(FundHop.hop_number).all()
    
    def get_fund_hops_by_address(self, address: str, as_source: bool = True) -> List[FundHop]:
        query = self.session.query(FundHop)
        if as_source:
            return query.filter(FundHop.from_address == address).all()
        return query.filter(FundHop.to_address == address).all()
    
    def save_market(self, market: Market) -> Market:
        existing = self.session.query(Market).filter(
            Market.condition_id == market.condition_id
        ).first()
        if existing:
            for key in ["question", "slug", "tokens", "closed"]:
                setattr(existing, key, getattr(market, key))
            self.session.commit()
            return existing
        self.session.add(market)
        self.session.commit()
        return market
    
    def get_market(self, condition_id: str) -> Optional[Market]:
        return self.session.query(Market).filter(
            Market.condition_id == condition_id
        ).first()
    
    def update_wallet_risk_score(self, address: str, score: float):
        wallet = self.get_wallet(address)
        if wallet:
            wallet.risk_score = score
            self.session.commit()
