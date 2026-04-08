import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch, PropertyMock
from sqlalchemy.orm import Session

from src.storage.postgres_store import PostgresStore
from src.models.database import Wallet, Trade, DetectionFlag, FundHop, Market


class TestPostgresStore:
    @pytest.fixture
    def store_with_mock_session(self):
        with patch('src.storage.postgres_store.get_session') as mock_get_session:
            mock_session = MagicMock(spec=Session)
            mock_get_session.return_value = mock_session
            
            store = PostgresStore()
            store.session = mock_session
            yield store, mock_session

    def test_init(self):
        with patch('src.storage.postgres_store.get_session') as mock_get_session:
            mock_session = MagicMock()
            mock_get_session.return_value = mock_session
            
            store = PostgresStore()
            
            assert store.session == mock_session

    def test_ensure_wallet_existing(self, store_with_mock_session):
        store, mock_session = store_with_mock_session
        
        existing_wallet = MagicMock(spec=Wallet)
        mock_session.query.return_value.filter.return_value.first.return_value = existing_wallet
        
        wallet = store.ensure_wallet("0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb5")
        
        assert wallet == existing_wallet
        mock_session.add.assert_not_called()

    def test_ensure_wallet_new(self, store_with_mock_session):
        store, mock_session = store_with_mock_session
        
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        wallet = store.ensure_wallet("0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb5")
        
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_get_wallet(self, store_with_mock_session):
        store, mock_session = store_with_mock_session
        
        expected_wallet = MagicMock(spec=Wallet)
        mock_session.query.return_value.filter.return_value.first.return_value = expected_wallet
        
        wallet = store.get_wallet("0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb5")
        
        assert wallet == expected_wallet

    def test_get_wallet_not_found(self, store_with_mock_session):
        store, mock_session = store_with_mock_session
        
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        wallet = store.get_wallet("0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb5")
        
        assert wallet is None

    def test_get_all_wallets(self, store_with_mock_session):
        store, mock_session = store_with_mock_session
        
        wallets = [MagicMock(spec=Wallet), MagicMock(spec=Wallet)]
        mock_session.query.return_value.all.return_value = wallets
        
        result = store.get_all_wallets()
        
        assert len(result) == 2

    def test_add_trade(self, store_with_mock_session):
        from src.models.schemas import Trade as TradeSchema
        
        store, mock_session = store_with_mock_session
        
        mock_session.query.return_value.filter.return_value.first.return_value = MagicMock()
        
        trade_schema = TradeSchema(
            tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            block_number=50000000,
            timestamp=datetime.now(),
            market_id="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb5",
            side="BUY",
            amount_usd=100.0
        )
        
        result = store.add_trade(trade_schema)
        
        mock_session.add.assert_called()
        mock_session.commit.assert_called()

    def test_add_trades_bulk(self, store_with_mock_session):
        store, mock_session = store_with_mock_session
        
        trades = [
            MagicMock(wallet_address="0x1111"),
            MagicMock(wallet_address="0x2222"),
            MagicMock(wallet_address="0x3333"),
        ]
        
        mock_session.query.return_value.filter.return_value.first.return_value = MagicMock()
        
        count = store.add_trades_bulk(trades)
        
        assert count == 3
        assert mock_session.add.call_count == 3
        mock_session.commit.assert_called_once()

    def test_get_trades_by_wallet(self, store_with_mock_session):
        store, mock_session = store_with_mock_session
        
        trades = [MagicMock(spec=Trade), MagicMock(spec=Trade)]
        mock_session.query.return_value.filter.return_value.all.return_value = trades
        
        result = store.get_trades_by_wallet("0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb5")
        
        assert len(result) == 2

    def test_get_trades_by_market(self, store_with_mock_session):
        store, mock_session = store_with_mock_session
        
        trades = [MagicMock(spec=Trade)]
        mock_session.query.return_value.filter.return_value.all.return_value = trades
        
        result = store.get_trades_by_market("0x1234567890abcdef")
        
        assert len(result) == 1

    def test_add_detection_flag(self, store_with_mock_session):
        store, mock_session = store_with_mock_session
        
        wallet = MagicMock(spec=Wallet)
        wallet.flags = {}
        mock_session.query.return_value.filter.return_value.first.return_value = wallet
        
        from src.models.schemas import DetectionFlag as DetectionFlagSchema
        flag_schema = DetectionFlagSchema(
            wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb5",
            flag_type="mixer_direct",
            confidence=95.0,
            evidence={"test": "data"},
            detected_at=datetime.now()
        )
        
        result = store.add_detection_flag(flag_schema)
        
        mock_session.add.assert_called()
        mock_session.commit.assert_called()

    def test_get_detection_flags(self, store_with_mock_session):
        store, mock_session = store_with_mock_session
        
        flags = [MagicMock(spec=DetectionFlag), MagicMock(spec=DetectionFlag)]
        mock_session.query.return_value.filter.return_value.all.return_value = flags
        
        result = store.get_detection_flags("0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb5")
        
        assert len(result) == 2

    def test_save_market_new(self, store_with_mock_session, sample_market):
        store, mock_session = store_with_mock_session
        
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        result = store.save_market(sample_market)
        
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called()

    def test_save_market_existing(self, store_with_mock_session, sample_market):
        store, mock_session = store_with_mock_session
        
        existing = MagicMock(spec=Market)
        mock_session.query.return_value.filter.return_value.first.return_value = existing
        
        result = store.save_market(sample_market)
        
        assert result == existing
        mock_session.add.assert_not_called()

    def test_update_wallet_risk_score(self, store_with_mock_session):
        store, mock_session = store_with_mock_session
        
        wallet = MagicMock(spec=Wallet)
        wallet.risk_score = 0.0
        mock_session.query.return_value.filter.return_value.first.return_value = wallet
        
        store.update_wallet_risk_score("0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb5", 75.5)
        
        assert wallet.risk_score == 75.5
        mock_session.commit.assert_called()

    def test_update_wallet_risk_score_wallet_not_found(self, store_with_mock_session):
        store, mock_session = store_with_mock_session
        
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        store.update_wallet_risk_score("0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb5", 75.5)
        
        mock_session.commit.assert_not_called()

    def test_close(self, store_with_mock_session):
        store, mock_session = store_with_mock_session
        
        store.close()
        
        mock_session.close.assert_called_once()


class TestGraphStore:
    def test_init_with_mock_settings(self):
        with patch('src.storage.graph_store.get_settings') as mock_get_settings:
            mock_settings = MagicMock()
            mock_settings.neo4j_uri = "bolt://localhost:7687"
            mock_settings.neo4j_user = "neo4j"
            mock_settings.neo4j_password = "test_password"
            mock_get_settings.return_value = mock_settings
            
            with patch('src.storage.graph_store.Graph') as mock_graph:
                from src.storage.graph_store import GraphStore
                
                store = GraphStore()
                
                mock_graph.assert_called_once()

    def test_clear_all(self):
        with patch('src.storage.graph_store.get_settings') as mock_get_settings:
            mock_settings = MagicMock()
            mock_settings.neo4j_uri = "bolt://localhost:7687"
            mock_settings.neo4j_user = "neo4j"
            mock_settings.neo4j_password = "test_password"
            mock_get_settings.return_value = mock_settings
            
            with patch('src.storage.graph_store.Graph') as mock_graph_class:
                from src.storage.graph_store import GraphStore
                
                mock_graph = MagicMock()
                mock_graph_class.return_value = mock_graph
                
                store = GraphStore()
                store.clear_all()
                
                mock_graph.delete_all.assert_called_once()

    def test_create_wallet_node(self):
        with patch('src.storage.graph_store.get_settings') as mock_get_settings:
            mock_settings = MagicMock()
            mock_settings.neo4j_uri = "bolt://localhost:7687"
            mock_settings.neo4j_user = "neo4j"
            mock_settings.neo4j_password = "test_password"
            mock_get_settings.return_value = mock_settings
            
            with patch('src.storage.graph_store.Graph') as mock_graph_class:
                from src.storage.graph_store import GraphStore
                
                mock_graph = MagicMock()
                mock_graph_class.return_value = mock_graph
                
                store = GraphStore()
                store.create_wallet_node("0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb5", total_trades=10)
                
                mock_graph.create.assert_called_once()

    def test_get_wallet_node(self):
        with patch('src.storage.graph_store.get_settings') as mock_get_settings:
            mock_settings = MagicMock()
            mock_settings.neo4j_uri = "bolt://localhost:7687"
            mock_settings.neo4j_user = "neo4j"
            mock_settings.neo4j_password = "test_password"
            mock_get_settings.return_value = mock_settings
            
            with patch('src.storage.graph_store.Graph') as mock_graph_class:
                from src.storage.graph_store import GraphStore
                
                mock_graph = MagicMock()
                mock_graph_class.return_value = mock_graph
                
                store = GraphStore()
                store.get_wallet_node("0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb5")
                
                mock_graph.nodes.match.assert_called_once()

    def test_create_mixer_node(self):
        with patch('src.storage.graph_store.get_settings') as mock_get_settings:
            mock_settings = MagicMock()
            mock_settings.neo4j_uri = "bolt://localhost:7687"
            mock_settings.neo4j_user = "neo4j"
            mock_settings.neo4j_password = "test_password"
            mock_get_settings.return_value = mock_settings
            
            with patch('src.storage.graph_store.Graph') as mock_graph_class:
                from src.storage.graph_store import GraphStore
                
                mock_graph = MagicMock()
                mock_graph_class.return_value = mock_graph
                
                store = GraphStore()
                store.create_mixer_node("0x91031bCf8b7a6282b7a8403f46B4a7c9B6B0555D", "tornado_cash")
                
                mock_graph.create.assert_called_once()

    def test_create_bridge_node(self):
        with patch('src.storage.graph_store.get_settings') as mock_get_settings:
            mock_settings = MagicMock()
            mock_settings.neo4j_uri = "bolt://localhost:7687"
            mock_settings.neo4j_user = "neo4j"
            mock_settings.neo4j_password = "test_password"
            mock_get_settings.return_value = mock_settings
            
            with patch('src.storage.graph_store.Graph') as mock_graph_class:
                from src.storage.graph_store import GraphStore
                
                mock_graph = MagicMock()
                mock_graph_class.return_value = mock_graph
                
                store = GraphStore()
                store.create_bridge_node("0xC564EE9f21c8C733732019Ca51bb6FA18EdA78A5", "multichain")
                
                mock_graph.create.assert_called_once()

    def test_get_suspicious_wallets(self):
        with patch('src.storage.graph_store.get_settings') as mock_get_settings:
            mock_settings = MagicMock()
            mock_settings.neo4j_uri = "bolt://localhost:7687"
            mock_settings.neo4j_user = "neo4j"
            mock_settings.neo4j_password = "test_password"
            mock_get_settings.return_value = mock_settings
            
            with patch('src.storage.graph_store.Graph') as mock_graph_class:
                from src.storage.graph_store import GraphStore
                
                mock_graph = MagicMock()
                mock_graph.run.return_value = []
                mock_graph_class.return_value = mock_graph
                
                store = GraphStore()
                results = store.get_suspicious_wallets(min_score=50)
                
                mock_graph.run.assert_called()
                assert isinstance(results, list)
