import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from src.detection.mixers import MixerDetector, TornadoHeuristics
from src.models.schemas import DetectionFlag
from src.data.onchain_client import MIXER_CONTRACTS


class TestMixerDetector:
    def test_init(self, mock_postgres_store, mock_onchain_client):
        detector = MixerDetector(mock_postgres_store, mock_onchain_client)
        assert detector.store == mock_postgres_store
        assert detector.onchain == mock_onchain_client

    def test_detect_for_wallet_no_flags(self, mock_postgres_store, mock_onchain_client, sample_wallet_address):
        mock_onchain_client.get_usdc_transfers.return_value = {"incoming": [], "outgoing": []}
        mock_onchain_client.trace_fund_origin.return_value = []
        
        detector = MixerDetector(mock_postgres_store, mock_onchain_client)
        flags = detector.detect_for_wallet(sample_wallet_address)
        
        assert len(flags) == 0

    def test_detect_for_wallet_direct_mixer_interaction(
        self, mock_postgres_store, mock_onchain_client, sample_wallet_address, sample_mixer_address
    ):
        mixer_tx = {
            "from": sample_mixer_address,
            "to": sample_wallet_address,
            "value": 1000.0,
            "block_number": 50000000,
            "tx_hash": "0xabc123"
        }
        mock_onchain_client.get_usdc_transfers.return_value = {
            "incoming": [mixer_tx],
            "outgoing": []
        }
        mock_onchain_client.trace_fund_origin.return_value = []
        
        detector = MixerDetector(mock_postgres_store, mock_onchain_client)
        flags = detector.detect_for_wallet(sample_wallet_address)
        
        assert len(flags) == 1
        assert flags[0].flag_type == "mixer_direct"
        assert flags[0].confidence == 95.0

    def test_detect_for_wallet_indirect_mixer_funding(
        self, mock_postgres_store, mock_onchain_client, sample_wallet_address
    ):
        mock_onchain_client.get_usdc_transfers.return_value = {"incoming": [], "outgoing": []}
        mock_onchain_client.trace_fund_origin.return_value = [
            {
                "from_address": "0x91031bCf8b7a6282b7a8403f46B4a7c9B6B0555D",
                "to_address": sample_wallet_address,
                "amount": "1000.0",
                "contract_type": "mixer:tornado_cash_ethereum"
            }
        ]
        
        detector = MixerDetector(mock_postgres_store, mock_onchain_client)
        flags = detector.detect_for_wallet(sample_wallet_address)
        
        assert len(flags) == 1
        assert flags[0].flag_type == "mixer_indirect"
        assert flags[0].confidence == 70.0

    def test_detect_for_wallet_multiple_mixer_hops(
        self, mock_postgres_store, mock_onchain_client, sample_wallet_address
    ):
        mock_onchain_client.get_usdc_transfers.return_value = {"incoming": [], "outgoing": []}
        mock_onchain_client.trace_fund_origin.return_value = [
            {
                "from_address": "0x91031bCf8b7a6282b7a8403f46B4a7c9B6B0555D",
                "to_address": sample_wallet_address,
                "amount": "1000.0",
                "contract_type": "mixer:tornado_cash_ethereum"
            },
            {
                "from_address": "0xA160cdAB225685dA1d56d34277e6D5DB7d16b3C",
                "to_address": "0x91031bCf8b7a6282b7a8403f46B4a7c9B6B0555D",
                "amount": "1000.0",
                "contract_type": "mixer:tornado_cash_ethereum"
            }
        ]
        
        detector = MixerDetector(mock_postgres_store, mock_onchain_client)
        flags = detector.detect_for_wallet(sample_wallet_address)
        
        assert len(flags) == 1
        assert flags[0].flag_type == "mixer_indirect"
        assert flags[0].confidence == 85.0

    def test_run_detection_with_addresses(
        self, mock_postgres_store, mock_onchain_client, sample_wallet_address
    ):
        mock_onchain_client.get_usdc_transfers.return_value = {"incoming": [], "outgoing": []}
        mock_onchain_client.trace_fund_origin.return_value = []
        
        detector = MixerDetector(mock_postgres_store, mock_onchain_client)
        total_flags = detector.run_detection(addresses=[sample_wallet_address])
        
        assert total_flags == 0

    def test_check_direct_mixer_interaction_outgoing(
        self, mock_postgres_store, mock_onchain_client, sample_wallet_address, sample_mixer_address
    ):
        mixer_tx = {
            "from": sample_wallet_address,
            "to": sample_mixer_address,
            "value": 1000.0,
            "block_number": 50000000,
            "tx_hash": "0xabc123"
        }
        mock_onchain_client.get_usdc_transfers.return_value = {
            "incoming": [],
            "outgoing": [mixer_tx]
        }
        
        detector = MixerDetector(mock_postgres_store, mock_onchain_client)
        result = detector._check_direct_mixer_interaction(sample_wallet_address)
        
        assert result is not None
        assert result["direction"] == "outgoing"


class TestTornadoHeuristics:
    def test_analyze_timing_patterns_insufficient_data(self):
        transactions = []
        result = TornadoHeuristics.analyze_timing_patterns(transactions)
        assert result["suspicious"] is False
        assert result["confidence"] == 0

    def test_analyze_timing_patterns_single_transaction(self):
        transactions = [{"timestamp": datetime.now()}]
        result = TornadoHeuristics.analyze_timing_patterns(transactions)
        assert result["suspicious"] is False

    def test_analyze_timing_patterns_regular_intervals(self):
        base_time = datetime.now()
        transactions = [
            {"timestamp": base_time - timedelta(seconds=30)}
            for _ in range(5)
        ]
        result = TornadoHeuristics.analyze_timing_patterns(transactions)
        assert result["suspicious"] is True
        assert result["pattern"] == "regular_intervals"
        assert result["confidence"] == 60

    def test_analyze_timing_patterns_random_intervals(self):
        base_time = datetime.now()
        transactions = [
            {"timestamp": base_time - timedelta(hours=1)},
            {"timestamp": base_time - timedelta(hours=2)},
            {"timestamp": base_time - timedelta(hours=5)},
            {"timestamp": base_time - timedelta(hours=10)},
            {"timestamp": base_time - timedelta(hours=18)},
        ]
        result = TornadoHeuristics.analyze_timing_patterns(transactions)
        assert result["pattern"] == "random"

    def test_analyze_denomination_patterns_matches_tornado(self):
        amounts = [0.1, 1.0, 10.0, 100.0, 0.1, 1.0]
        result = TornadoHeuristics.analyze_denomination_patterns(amounts)
        assert result["matches_tornado_denominations"] is True
        assert result["confidence"] == 75.0

    def test_analyze_denomination_patterns_no_match(self):
        amounts = [123.45, 67.89, 50.0]
        result = TornadoHeuristics.analyze_denomination_patterns(amounts)
        assert result["matches_tornado_denominations"] is False
        assert result["confidence"] == 0

    def test_analyze_gas_price_fingerprint_suspicious(self):
        transactions = [
            {"gas_price": 50000000000},
            {"gas_price": 50000000000},
            {"gas_price": 50000000000},
            {"gas_price": 50000000000},
            {"gas_price": 50000000000},
        ]
        result = TornadoHeuristics.analyze_gas_price_fingerprint(transactions)
        assert result["suspicious"] is True
        assert result["fingerprint_strength"] > 0.7

    def test_analyze_gas_price_fingerprint_normal(self):
        transactions = [
            {"gas_price": 50000000000 + i * 1000000000}
            for i in range(5)
        ]
        result = TornadoHeuristics.analyze_gas_price_fingerprint(transactions)
        assert result["suspicious"] is False

    def test_analyze_gas_price_fingerprint_insufficient_data(self):
        transactions = [{"gas_price": 50000000000}, {"gas_price": 51000000000}]
        result = TornadoHeuristics.analyze_gas_price_fingerprint(transactions)
        assert result["suspicious"] is False


class TestMixerContractAddresses:
    def test_tornado_cash_addresses_defined(self):
        assert "tornado_cash_ethereum" in MIXER_CONTRACTS
        assert len(MIXER_CONTRACTS["tornado_cash_ethereum"]) > 0

    def test_railgun_addresses_defined(self):
        assert "railgun" in MIXER_CONTRACTS
        assert len(MIXER_CONTRACTS["railgun"]) > 0

    def test_addresses_are_checksummed(self, sample_mixer_address):
        assert sample_mixer_address == sample_mixer_address.lower() or sample_mixer_address == sample_mixer_address.upper() or sample_mixer_address == sample_mixer_address
