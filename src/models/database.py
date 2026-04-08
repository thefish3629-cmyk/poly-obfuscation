from sqlalchemy import create_engine, Column, String, Integer, BigInteger, Float, DateTime, Text, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from ..utils.config import get_settings

Base = declarative_base()


class Wallet(Base):
    __tablename__ = "wallets"
    
    address = Column(String(42), primary_key=True)
    first_seen = Column(DateTime, nullable=True)
    total_trades = Column(Integer, default=0)
    total_volume_usd = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.0)
    flags = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.now)


class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tx_hash = Column(String(66), nullable=False)
    block_number = Column(BigInteger, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    market_id = Column(String(128), nullable=False)
    wallet_address = Column(String(42), nullable=False)
    side = Column(String(4), nullable=False)
    amount_usd = Column(Float, nullable=False)
    outcome_token_id = Column(String(128), nullable=True)
    maker = Column(String(42), nullable=True)
    taker = Column(String(42), nullable=True)
    
    __table_args__ = (
        Index("idx_wallet_address", "wallet_address"),
        Index("idx_market_id", "market_id"),
        Index("idx_timestamp", "timestamp"),
    )


class DetectionFlag(Base):
    __tablename__ = "detection_flags"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    wallet_address = Column(String(42), nullable=False)
    flag_type = Column(String(32), nullable=False)
    confidence = Column(Float, nullable=False)
    evidence = Column(JSON, default=dict)
    detected_at = Column(DateTime, default=datetime.now)
    
    __table_args__ = (
        Index("idx_detection_wallet", "wallet_address"),
        Index("idx_flag_type", "flag_type"),
    )


class FundHop(Base):
    __tablename__ = "fund_hops"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    trace_id = Column(String(64), nullable=False)
    from_address = Column(String(42), nullable=False)
    to_address = Column(String(42), nullable=False)
    token = Column(String(32), nullable=False)
    amount = Column(String(50), nullable=False)
    contract_type = Column(String(32), nullable=False)
    hop_number = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
    __table_args__ = (
        Index("idx_trace_id", "trace_id"),
        Index("idx_fund_from", "from_address"),
        Index("idx_fund_to", "to_address"),
    )


class Market(Base):
    __tablename__ = "markets"
    
    condition_id = Column(String(128), primary_key=True)
    question = Column(Text, nullable=False)
    slug = Column(String(128), nullable=False)
    tokens = Column(JSON, default=list)
    closed = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    
    def __init__(self, **kwargs):
        if 'closed' in kwargs:
            kwargs['closed'] = 1 if kwargs['closed'] else 0
        if 'tokens' in kwargs and isinstance(kwargs['tokens'], list):
            kwargs['tokens'] = str(kwargs['tokens'])
        super().__init__(**kwargs)


def get_engine():
    settings = get_settings()
    url = f"postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
    return create_engine(url, pool_pre_ping=True)


def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def init_db():
    engine = get_engine()
    Base.metadata.create_all(engine)
