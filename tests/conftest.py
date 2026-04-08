import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.database import Base, Wallet, Trade, DetectionFlag, FundHop, Market
from src.models.schemas import Trade as TradeSchema, DetectionFlag as DetectionFlagSchema


@pytest.fixture
def mock_settings():
    settings = MagicMock()
    settings.polygon_rpc_url = "https://mock-rpc.example.com"
    settings.dune_api_key = "test_dune_key"
    settings.goldsky_api_key = "test_goldsky_key"
    settings.postgres_host = "localhost"
    settings.postgres_port = 5432
    settings.postgres_user = "test_user"
    settings.postgres_password = "test_password"
    settings.postgres_db = "test_db"
    settings.neo4j_uri = "bolt://localhost:7687"
    settings.neo4j_user = "neo4j"
    settings.neo4j_password = "test_password"
    return settings


@pytest.fixture
def sample_wallet_address():
    return "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb5"


@pytest.fixture
def sample_trader_address():
    return "0x8626f6940E2eb28930eFb4CeF49B2d1F2C9C1199"


@pytest.fixture
def sample_mixer_address():
    return "0x91031bCf8b7a6282b7a8403f46B4a7c9B6B0555D"


@pytest.fixture
def sample_bridge_address():
    return "0xC564EE9f21c8C733732019Ca51bb6FA18EdA78A5"


@pytest.fixture
def sample_market_condition_id():
    return "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"


@pytest.fixture
def sample_wallet():
    return Wallet(
        address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb5",
        first_seen=datetime.now() - timedelta(days=30),
        total_trades=10,
        total_volume_usd=5000.0,
        risk_score=25.0,
        flags={"mixer_indirect": 60.0}
    )


@pytest.fixture
def sample_trade():
    return Trade(
        id=1,
        tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        block_number=50000000,
        timestamp=datetime.now() - timedelta(hours=1),
        market_id="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb5",
        side="BUY",
        amount_usd=100.0,
        outcome_token_id="0xtoken123",
        maker="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb5",
        taker="0x8626f6940E2eb28930eFb4CeF49B2d1F2C9C1199"
    )


@pytest.fixture
def sample_trades_batch():
    base_time = datetime.now()
    return [
        Trade(
            id=i,
            tx_hash=f"0x{'a' * 64}",
            block_number=50000000 + i,
            timestamp=base_time - timedelta(hours=i),
            market_id="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            wallet_address=f"0x{'1' * 40}",
            side="BUY" if i % 2 == 0 else "SELL",
            amount_usd=100.0 * (i + 1),
        )
        for i in range(10)
    ]


@pytest.fixture
def sample_detection_flag():
    return DetectionFlag(
        id=1,
        wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb5",
        flag_type="mixer_direct",
        confidence=95.0,
        evidence={"mixer_type": "tornado_cash", "tx_hash": "0xabc123"},
        detected_at=datetime.now()
    )


@pytest.fixture
def sample_detection_flags():
    return [
        DetectionFlagSchema(
            wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb5",
            flag_type="mixer_direct",
            confidence=95.0,
            evidence={"mixer_type": "tornado_cash"},
            detected_at=datetime.now()
        ),
        DetectionFlagSchema(
            wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb5",
            flag_type="bridge_direct",
            confidence=85.0,
            evidence={"bridge_type": "multichain"},
            detected_at=datetime.now()
        ),
        DetectionFlagSchema(
            wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb5",
            flag_type="sybil_cluster",
            confidence=75.0,
            evidence={"cluster_size": 3},
            detected_at=datetime.now()
        ),
    ]


@pytest.fixture
def sample_fund_hops():
    return [
        FundHop(
            id=1,
            trace_id="trace_001",
            from_address="0x91031bCf8b7a6282b7a8403f46B4a7c9B6B0555D",
            to_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb5",
            token="USDC",
            amount="1000.0",
            contract_type="mixer:tornado_cash_ethereum",
            hop_number=1,
            timestamp=datetime.now() - timedelta(hours=2)
        ),
        FundHop(
            id=2,
            trace_id="trace_001",
            from_address="0xC564EE9f21c8C733732019Ca51bb6FA18EdA78A5",
            to_address="0x91031bCf8b7a6282b7a8403f46B4a7c9B6B0555D",
            token="USDC",
            amount="1000.0",
            contract_type="bridge:multichain_anywap",
            hop_number=2,
            timestamp=datetime.now() - timedelta(hours=3)
        ),
    ]


@pytest.fixture
def sample_market():
    return Market(
        condition_id="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        question="Israel strike on Iranian nuclear facility before July?",
        slug="israel-strike-iran-nuclear-facility-before-july",
        tokens=["0xtoken1", "0xtoken2"],
        closed=0
    )


@pytest.fixture
def mock_onchain_client():
    from src.data.onchain_client import OnchainClient
    
    with patch.object(OnchainClient, '__init__', lambda self, rpc_url=None: None):
        client = MagicMock(spec=OnchainClient)
        client.rpc_url = "https://mock-rpc.example.com"
        client.w3 = MagicMock()
        client.usdc_contract = MagicMock()
        
        client.get_usdc_transfers.return_value = {
            "incoming": [
                {
                    "from": "0x91031bCf8b7a6282b7a8403f46B4a7c9B6B0555D",
                    "to": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb5",
                    "value": 1000.0,
                    "block_number": 50000000,
                    "tx_hash": "0xabc123"
                }
            ],
            "outgoing": []
        }
        
        client.trace_fund_origin.return_value = [
            {
                "trace_id": "trace_001",
                "from_address": "0x91031bCf8b7a6282b7a8403f46B4a7c9B6B0555D",
                "to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb5",
                "token": "USDC",
                "amount": "1000.0",
                "contract_type": "mixer:tornado_cash_ethereum",
                "hop_number": 1,
                "timestamp": datetime.now(),
                "tx_hash": "0xabc123"
            }
        ]
        
        client.get_contract_type.return_value = "wallet"
        
        return client


@pytest.fixture
def mock_postgres_store():
    from src.storage.postgres_store import PostgresStore
    
    with patch.object(PostgresStore, '__init__', lambda self: None):
        store = MagicMock(spec=PostgresStore)
        store.session = MagicMock()
        
        return store
