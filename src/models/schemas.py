from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class Wallet(BaseModel):
    address: str
    first_seen: Optional[datetime] = None
    total_trades: int = 0
    total_volume_usd: float = 0.0
    risk_score: float = 0.0
    flags: dict = Field(default_factory=dict)


class Trade(BaseModel):
    id: Optional[int] = None
    tx_hash: str
    block_number: int
    timestamp: datetime
    market_id: str
    wallet_address: str
    side: str
    amount_usd: float
    outcome_token_id: Optional[str] = None
    maker: Optional[str] = None
    taker: Optional[str] = None


class Market(BaseModel):
    condition_id: str
    question: str
    slug: str
    tokens: List[str] = []
    closed: int = 0


class DetectionFlag(BaseModel):
    wallet_address: str
    flag_type: str
    confidence: float
    evidence: dict
    detected_at: datetime = Field(default_factory=datetime.now)


class FundHop(BaseModel):
    trace_id: str
    from_address: str
    to_address: str
    token: str
    amount: float
    contract_type: str
    hop_number: int
    timestamp: datetime


class RiskScore(BaseModel):
    wallet_address: str
    total_score: float
    mixer_score: float = 0.0
    bridge_score: float = 0.0
    sybil_score: float = 0.0
    layering_score: float = 0.0
    details: dict = Field(default_factory=dict)
