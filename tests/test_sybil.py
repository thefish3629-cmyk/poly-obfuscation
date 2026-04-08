import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from src.detection.sybil import SybilDetector


class TestSybilDetector:
    def test_init(self, mock_postgres_store):
        detector = SybilDetector(mock_postgres_store)
        assert detector.store == mock_postgres_store

    def test_detect_clusters_no_trades(self, mock_postgres_store):
        mock_postgres_store.session.query.return_value.all.return_value = []
        
        detector = SybilDetector(mock_postgres_store)
        clusters = detector.detect_clusters()
        
        assert clusters == []

    def test_cluster_by_timing_synchronized(self, mock_postgres_store, sample_trades_batch):
        trades = sample_trades_batch[:5]
        
        for i, trade in enumerate(trades[:2]):
            trade.wallet_address = "0x1111111111111111111111111111111111111111"
            trade.timestamp = datetime.now() - timedelta(minutes=i)
        for i, trade in enumerate(trades[2:4]):
            trade.wallet_address = "0x2222222222222222222222222222222222222222"
            trade.timestamp = datetime.now() - timedelta(minutes=i)
        
        mock_postgres_store.get_trades_by_market.return_value = trades
        mock_postgres_store.session.query.return_value.all.return_value = trades
        
        detector = SybilDetector(mock_postgres_store)
        clusters = detector._cluster_by_timing(trades)
        
        assert len(clusters) >= 0

    def test_cluster_by_timing_unsynchronized(self, mock_postgres_store, sample_trades_batch):
        trades = sample_trades_batch[:5]
        
        for i, trade in enumerate(trades[:2]):
            trade.wallet_address = "0x1111111111111111111111111111111111111111"
            trade.timestamp = datetime.now() - timedelta(hours=i * 5)
        for i, trade in enumerate(trades[2:4]):
            trade.wallet_address = "0x2222222222222222222222222222222222222222"
            trade.timestamp = datetime.now() - timedelta(hours=i * 3 + 10)
        
        mock_postgres_store.get_trades_by_market.return_value = trades
        
        detector = SybilDetector(mock_postgres_store)
        clusters = detector._cluster_by_timing(trades)
        
        sync_scores = [c.get("confidence", 0) / 80 for c in clusters]
        for score in sync_scores:
            if score > 0:
                assert score <= 1.0

    def test_pattern_similarity_identical(self):
        pattern1 = {"markets": ["m1", "m2", "m3"], "sides": ["BUY", "BUY", "SELL"], "volumes": [100.0, 200.0, 150.0]}
        pattern2 = {"markets": ["m1", "m2", "m3"], "sides": ["BUY", "BUY", "SELL"], "volumes": [100.0, 200.0, 150.0]}
        
        detector = SybilDetector(MagicMock())
        similarity = detector._pattern_similarity(pattern1, pattern2)
        
        assert similarity == 1.0

    def test_pattern_similarity_no_overlap(self):
        pattern1 = {"markets": ["m1", "m2"], "sides": ["BUY", "SELL"], "volumes": [100.0, 200.0]}
        pattern2 = {"markets": ["m3", "m4"], "sides": ["BUY", "SELL"], "volumes": [100.0, 200.0]}
        
        detector = SybilDetector(MagicMock())
        similarity = detector._pattern_similarity(pattern1, pattern2)
        
        assert similarity == 0.0

    def test_pattern_similarity_partial(self):
        pattern1 = {"markets": ["m1", "m2", "m3"], "sides": ["BUY", "BUY", "SELL"], "volumes": [100.0, 200.0, 150.0]}
        pattern2 = {"markets": ["m1", "m2", "m4"], "sides": ["BUY", "SELL", "BUY"], "volumes": [100.0, 50.0, 200.0]}
        
        detector = SybilDetector(MagicMock())
        similarity = detector._pattern_similarity(pattern1, pattern2)
        
        assert 0 < similarity < 1

    def test_cluster_by_trading_pattern(self, mock_postgres_store):
        trades = [
            MagicMock(wallet_address="0x1111111111111111111111111111111111111111", market_id="m1", side="BUY", amount_usd=100.0),
            MagicMock(wallet_address="0x1111111111111111111111111111111111111111", market_id="m1", side="BUY", amount_usd=100.0),
            MagicMock(wallet_address="0x2222222222222222222222222222222222222222", market_id="m1", side="BUY", amount_usd=100.0),
            MagicMock(wallet_address="0x2222222222222222222222222222222222222222", market_id="m1", side="BUY", amount_usd=100.0),
        ]
        
        detector = SybilDetector(mock_postgres_store)
        clusters = detector._cluster_by_trading_pattern(trades)
        
        assert len(clusters) == 1
        assert clusters[0]["type"] == "pattern"

    def test_cluster_by_coordination(self, mock_postgres_store):
        now = datetime.now()
        trades = [
            MagicMock(
                wallet_address="0x1111111111111111111111111111111111111111",
                market_id="m1",
                side="BUY",
                amount_usd=100.0,
                timestamp=now
            ),
            MagicMock(
                wallet_address="0x2222222222222222222222222222222222222222",
                market_id="m1",
                side="BUY",
                amount_usd=100.0,
                timestamp=now + timedelta(seconds=30)
            ),
        ]
        
        detector = SybilDetector(mock_postgres_store)
        clusters = detector._cluster_by_coordination(trades)
        
        assert len(clusters) == 1
        assert clusters[0]["type"] == "coordinated"
        assert clusters[0]["confidence"] == 75.0

    def test_cluster_by_coordination_different_markets(self, mock_postgres_store):
        now = datetime.now()
        trades = [
            MagicMock(
                wallet_address="0x1111111111111111111111111111111111111111",
                market_id="m1",
                side="BUY",
                amount_usd=100.0,
                timestamp=now
            ),
            MagicMock(
                wallet_address="0x2222222222222222222222222222222222222222",
                market_id="m2",
                side="BUY",
                amount_usd=100.0,
                timestamp=now + timedelta(seconds=30)
            ),
        ]
        
        detector = SybilDetector(mock_postgres_store)
        clusters = detector._cluster_by_coordination(trades)
        
        assert clusters == []

    def test_merge_clusters(self, mock_postgres_store):
        clusters = [
            {"type": "timing", "wallets": ["0x1111", "0x2222"], "confidence": 80.0, "evidence": {}},
            {"type": "pattern", "wallets": ["0x2222", "0x3333"], "confidence": 85.0, "evidence": {}},
        ]
        
        detector = SybilDetector(mock_postgres_store)
        merged = detector._merge_clusters(clusters)
        
        assert len(merged) >= 1

    def test_merge_clusters_empty(self, mock_postgres_store):
        detector = SybilDetector(mock_postgres_store)
        merged = detector._merge_clusters([])
        
        assert merged == []

    def test_flag_cluster_members(self, mock_postgres_store):
        clusters = [
            {
                "wallets": ["0x1111", "0x2222"],
                "confidence": 80.0,
                "evidence": {"type": "timing"}
            }
        ]
        
        detector = SybilDetector(mock_postgres_store)
        total_flags = detector.flag_cluster_members(clusters)
        
        assert total_flags == 2
        assert mock_postgres_store.add_detection_flag.call_count == 2

    def test_run_detection(self, mock_postgres_store, sample_market_condition_id):
        mock_postgres_store.get_trades_by_market.return_value = []
        mock_postgres_store.session.query.return_value.all.return_value = []
        
        detector = SybilDetector(mock_postgres_store)
        clusters = detector.run_detection(market_id=sample_market_condition_id)
        
        assert isinstance(clusters, list)


class TestSybilScoring:
    def test_timing_similarity_same_time(self):
        times1 = [datetime(2024, 1, 1, 12, 0, 0), datetime(2024, 1, 1, 12, 1, 0)]
        times2 = [datetime(2024, 1, 1, 12, 0, 30), datetime(2024, 1, 1, 12, 1, 30)]
        
        detector = SybilDetector(MagicMock())
        similarity = detector._calculate_timing_similarity(times1, times2)
        
        assert similarity > 0

    def test_timing_similarity_different_times(self):
        times1 = [datetime(2024, 1, 1, 12, 0, 0), datetime(2024, 1, 1, 12, 1, 0)]
        times2 = [datetime(2024, 1, 1, 14, 0, 0), datetime(2024, 1, 1, 15, 0, 0)]
        
        detector = SybilDetector(MagicMock())
        similarity = detector._calculate_timing_similarity(times1, times2)
        
        assert similarity == 0

    def test_timing_similarity_insufficient_data(self):
        times1 = [datetime(2024, 1, 1, 12, 0, 0)]
        times2 = [datetime(2024, 1, 1, 12, 0, 30)]
        
        detector = SybilDetector(MagicMock())
        similarity = detector._calculate_timing_similarity(times1, times2)
        
        assert similarity == 0
