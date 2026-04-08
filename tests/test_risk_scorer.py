import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from src.analysis.risk_scorer import RiskScorer, RISK_WEIGHTS
from src.models.schemas import RiskScore


class TestRiskScorer:
    def test_init(self, mock_postgres_store):
        scorer = RiskScorer(mock_postgres_store)
        assert scorer.store == mock_postgres_store

    def test_calculate_wallet_score_no_flags(self, mock_postgres_store, sample_wallet_address):
        mock_postgres_store.get_detection_flags.return_value = []
        
        scorer = RiskScorer(mock_postgres_store)
        score = scorer.calculate_wallet_score(sample_wallet_address)
        
        assert score.wallet_address == sample_wallet_address
        assert score.total_score == 0.0

    def test_calculate_wallet_score_single_flag(
        self, mock_postgres_store, sample_wallet_address, sample_detection_flag
    ):
        mock_postgres_store.get_detection_flags.return_value = [sample_detection_flag]
        
        scorer = RiskScorer(mock_postgres_store)
        score = scorer.calculate_wallet_score(sample_wallet_address)
        
        expected_contribution = RISK_WEIGHTS["mixer_direct"] * (95.0 / 100.0)
        assert score.mixer_score == expected_contribution
        assert score.total_score == expected_contribution

    def test_calculate_wallet_score_multiple_flags(
        self, mock_postgres_store, sample_wallet_address, sample_detection_flags
    ):
        mock_postgres_store.get_detection_flags.return_value = sample_detection_flags
        
        scorer = RiskScorer(mock_postgres_store)
        score = scorer.calculate_wallet_score(sample_wallet_address)
        
        assert score.mixer_score > 0
        assert score.bridge_score > 0
        assert score.sybil_score > 0
        assert score.total_score > 0

    def test_calculate_wallet_score_caps_at_100(
        self, mock_postgres_store, sample_wallet_address
    ):
        high_confidence_flags = [
            MagicMock(flag_type="mixer_direct", confidence=100.0),
            MagicMock(flag_type="bridge_direct", confidence=100.0),
            MagicMock(flag_type="sybil_cluster", confidence=100.0),
            MagicMock(flag_type="layering_fan_pattern", confidence=100.0),
        ]
        mock_postgres_store.get_detection_flags.return_value = high_confidence_flags
        
        scorer = RiskScorer(mock_postgres_store)
        score = scorer.calculate_wallet_score(sample_wallet_address)
        
        assert score.total_score <= 100.0

    def test_calculate_wallet_score_takes_max_per_category(
        self, mock_postgres_store, sample_wallet_address
    ):
        mixer_flags = [
            MagicMock(flag_type="mixer_direct", confidence=60.0),
            MagicMock(flag_type="mixer_indirect", confidence=90.0),
        ]
        mock_postgres_store.get_detection_flags.return_value = mixer_flags
        
        scorer = RiskScorer(mock_postgres_store)
        score = scorer.calculate_wallet_score(sample_wallet_address)
        
        expected = RISK_WEIGHTS["mixer_direct"] * (60.0 / 100.0)
        assert score.mixer_score == expected

    def test_calculate_all_scores(self, mock_postgres_store):
        wallets = [
            MagicMock(address="0x1111111111111111111111111111111111111111", risk_score=0.0),
            MagicMock(address="0x2222222222222222222222222222222222222222", risk_score=25.0),
        ]
        mock_postgres_store.get_all_wallets.return_value = wallets
        mock_postgres_store.get_detection_flags.return_value = []
        
        scorer = RiskScorer(mock_postgres_store)
        scores = scorer.calculate_all_scores()
        
        assert len(scores) == 2
        assert scores[0].wallet_address == "0x1111111111111111111111111111111111111111"
        assert scores[1].wallet_address == "0x2222222222222222222222222222222222222222"

    def test_calculate_all_scores_sorted_descending(self, mock_postgres_store):
        wallets = [
            MagicMock(address="0x1111111111111111111111111111111111111111", risk_score=10.0),
            MagicMock(address="0x2222222222222222222222222222222222222222", risk_score=50.0),
        ]
        mock_postgres_store.get_all_wallets.return_value = wallets
        mock_postgres_store.get_detection_flags.side_effect = lambda addr: [
            MagicMock(flag_type="bridge_direct", confidence=90.0)
        ] if addr == "0x2222222222222222222222222222222222222222" else []
        
        scorer = RiskScorer(mock_postgres_store)
        scores = scorer.calculate_all_scores()
        
        assert scores[0].total_score >= scores[1].total_score

    def test_get_risk_distribution(self, mock_postgres_store):
        wallets = [
            MagicMock(risk_score=10.0),
            MagicMock(risk_score=20.0),
            MagicMock(risk_score=30.0),
            MagicMock(risk_score=55.0),
            MagicMock(risk_score=80.0),
        ]
        mock_postgres_store.get_all_wallets.return_value = wallets
        
        scorer = RiskScorer(mock_postgres_store)
        dist = scorer.get_risk_distribution()
        
        assert dist["total_wallets"] == 5
        assert dist["low_risk"]["count"] == 2
        assert dist["medium_risk"]["count"] == 1
        assert dist["high_risk"]["count"] == 1
        assert dist["critical_risk"]["count"] == 1

    def test_get_risk_distribution_empty(self, mock_postgres_store):
        mock_postgres_store.get_all_wallets.return_value = []
        
        scorer = RiskScorer(mock_postgres_store)
        dist = scorer.get_risk_distribution()
        
        assert dist["total_wallets"] == 0

    def test_get_flagged_wallets(self, mock_postgres_store):
        wallets = [
            MagicMock(address="0x1111", risk_score=10.0),
            MagicMock(address="0x2222", risk_score=30.0),
            MagicMock(address="0x3333", risk_score=60.0),
        ]
        mock_postgres_store.get_all_wallets.return_value = wallets
        mock_postgres_store.get_detection_flags.return_value = []
        
        scorer = RiskScorer(mock_postgres_store)
        flagged = scorer.get_flagged_wallets(min_score=25)
        
        assert len(flagged) == 2

    def test_get_flagged_wallets_sorted_by_score(self, mock_postgres_store):
        wallets = [
            MagicMock(address="0x1111", risk_score=30.0),
            MagicMock(address="0x2222", risk_score=80.0),
            MagicMock(address="0x3333", risk_score=55.0),
        ]
        mock_postgres_store.get_all_wallets.return_value = wallets
        mock_postgres_store.get_detection_flags.return_value = []
        
        scorer = RiskScorer(mock_postgres_store)
        flagged = scorer.get_flagged_wallets(min_score=25)
        
        assert flagged[0]["address"] == "0x2222"
        assert flagged[1]["address"] == "0x3333"
        assert flagged[2]["address"] == "0x1111"


class TestRiskWeights:
    def test_risk_weights_defined(self):
        assert RISK_WEIGHTS is not None
        assert len(RISK_WEIGHTS) > 0

    def test_risk_weights_positive(self):
        for weight in RISK_WEIGHTS.values():
            assert weight > 0

    def test_risk_weights_mixer_direct_highest(self):
        assert RISK_WEIGHTS["mixer_direct"] == 40.0

    def test_risk_weights_sybil_cluster_high(self):
        assert RISK_WEIGHTS["sybil_cluster"] == 25.0

    def test_risk_weights_layering_circular_high(self):
        assert RISK_WEIGHTS["layering_circular"] == 25.0

    def test_risk_weights_bridge_direct_lower(self):
        assert RISK_WEIGHTS["bridge_direct"] == 15.0

    def test_risk_weights_chain_hopping_lower(self):
        assert RISK_WEIGHTS["chain_hopping"] == 10.0


class TestRiskScoreModel:
    def test_risk_score_model_creation(self):
        score = RiskScore(
            wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb5",
            total_score=65.5,
            mixer_score=30.0,
            bridge_score=15.0,
            sybil_score=20.0,
            layering_score=0.5,
            details={"flag_count": 3}
        )
        
        assert score.wallet_address == "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb5"
        assert score.total_score == 65.5
        assert score.details["flag_count"] == 3

    def test_risk_score_model_defaults(self):
        score = RiskScore(
            wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb5",
            total_score=0.0
        )
        
        assert score.mixer_score == 0.0
        assert score.bridge_score == 0.0
        assert score.sybil_score == 0.0
        assert score.layering_score == 0.0
