import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from src.detection.bridges import BridgeDetector, BridgeActivityAnalyzer
from src.data.onchain_client import BRIDGE_CONTRACTS


class TestBridgeDetector:
    def test_init(self, mock_postgres_store, mock_onchain_client):
        detector = BridgeDetector(mock_postgres_store, mock_onchain_client)
        assert detector.store == mock_postgres_store
        assert detector.onchain == mock_onchain_client
        assert detector.KNOWN_BRIDGES == BRIDGE_CONTRACTS

    def test_detect_for_wallet_no_bridges(self, mock_postgres_store, mock_onchain_client, sample_wallet_address):
        mock_onchain_client.get_usdc_transfers.return_value = {"incoming": [], "outgoing": []}
        mock_onchain_client.trace_fund_origin.return_value = []
        
        detector = BridgeDetector(mock_postgres_store, mock_onchain_client)
        flags = detector.detect_for_wallet(sample_wallet_address)
        
        assert len(flags) == 0

    def test_detect_for_wallet_direct_bridge_interaction(
        self, mock_postgres_store, mock_onchain_client, sample_wallet_address, sample_bridge_address
    ):
        mock_onchain_client.get_usdc_transfers.return_value = {
            "incoming": [
                {
                    "from": sample_bridge_address,
                    "to": sample_wallet_address,
                    "value": 5000.0,
                    "block_number": 50000000,
                    "tx_hash": "0xbridge123"
                }
            ],
            "outgoing": []
        }
        mock_onchain_client.get_contract_type.return_value = "bridge:multichain_anywap"
        mock_onchain_client.trace_fund_origin.return_value = []
        
        detector = BridgeDetector(mock_postgres_store, mock_onchain_client)
        flags = detector.detect_for_wallet(sample_wallet_address)
        
        assert len(flags) >= 1
        bridge_flags = [f for f in flags if f.flag_type == "bridge_direct"]
        assert len(bridge_flags) == 1
        assert bridge_flags[0].confidence == 90.0

    def test_detect_for_wallet_chain_hopping(
        self, mock_postgres_store, mock_onchain_client, sample_wallet_address, sample_bridge_address
    ):
        mock_onchain_client.get_usdc_transfers.return_value = {"incoming": [], "outgoing": []}
        mock_onchain_client.trace_fund_origin.return_value = [
            {
                "from_address": sample_bridge_address,
                "to_address": sample_wallet_address,
                "amount": "5000.0",
                "contract_type": "bridge:stargate"
            },
            {
                "from_address": "0x296F55F8Fb28E498B858d0BcDA06D955B2Cb3f4E",
                "to_address": sample_bridge_address,
                "amount": "5000.0",
                "contract_type": "bridge:stargate"
            }
        ]
        
        detector = BridgeDetector(mock_postgres_store, mock_onchain_client)
        flags = detector.detect_for_wallet(sample_wallet_address)
        
        chain_hopping_flags = [f for f in flags if f.flag_type == "chain_hopping"]
        assert len(chain_hopping_flags) == 1
        assert chain_hopping_flags[0].confidence == 75.0

    def test_check_direct_bridge_interaction_outgoing(
        self, mock_postgres_store, mock_onchain_client, sample_wallet_address, sample_bridge_address
    ):
        mock_onchain_client.get_usdc_transfers.return_value = {
            "incoming": [],
            "outgoing": [
                {
                    "from": sample_wallet_address,
                    "to": sample_bridge_address,
                    "value": 5000.0,
                    "block_number": 50000000,
                    "tx_hash": "0xbridge123"
                }
            ]
        }
        mock_onchain_client.get_contract_type.return_value = "bridge:multichain_anywap"
        
        detector = BridgeDetector(mock_postgres_store, mock_onchain_client)
        flags = detector._check_direct_bridge_interaction(sample_wallet_address)
        
        assert len(flags) == 1
        assert flags[0]["direction"] == "sent"

    def test_run_detection(self, mock_postgres_store, mock_onchain_client, sample_wallet_address):
        mock_onchain_client.get_usdc_transfers.return_value = {"incoming": [], "outgoing": []}
        mock_onchain_client.trace_fund_origin.return_value = []
        
        detector = BridgeDetector(mock_postgres_store, mock_onchain_client)
        total_flags = detector.run_detection(addresses=[sample_wallet_address])
        
        assert total_flags == 0


class TestBridgeActivityAnalyzer:
    def test_analyze_bridge_frequency_no_transactions(self):
        result = BridgeActivityAnalyzer.analyze_bridge_frequency([])
        assert result["suspicious"] is False
        assert result["confidence"] == 0

    def test_analyze_bridge_frequency_multiple_bridges(self):
        transactions = [
            {"contract_address": "0xC564EE9f21c8C733732019Ca51bb6FA18EdA78A5"},
            {"contract_address": "0xdf0770dF86a8034b3EFEf0A1Bb3c889B8332FF56"},
            {"contract_address": "0x296F55F8Fb28E498B858d0BcDA06D955B2Cb3f4E"},
            {"contract_address": "0xb6319cC6E9650A86F0cD1c817AbC76C91F9c5d4E"},
        ]
        result = BridgeActivityAnalyzer.analyze_bridge_frequency(transactions)
        assert result["suspicious"] is True
        assert result["unique_bridges_used"] >= 3
        assert result["confidence"] == 70

    def test_analyze_bridge_frequency_normal(self):
        transactions = [
            {"contract_address": "0xC564EE9f21c8C733732019Ca51bb6FA18EdA78A5"},
            {"contract_address": "0xC564EE9f21c8C733732019Ca51bb6FA18EdA78A5"},
        ]
        result = BridgeActivityAnalyzer.analyze_bridge_frequency(transactions)
        assert result["suspicious"] is False

    def test_analyze_bridge_amounts_large(self):
        transactions = [
            {"amount": 60000.0},
            {"amount": 100.0},
            {"amount": 75000.0},
        ]
        result = BridgeActivityAnalyzer.analyze_bridge_amounts(transactions)
        assert result["large_bridges_detected"] is True
        assert result["large_amount_count"] == 2
        assert result["confidence"] == 65

    def test_analyze_bridge_amounts_normal(self):
        transactions = [
            {"amount": 1000.0},
            {"amount": 500.0},
            {"amount": 2500.0},
        ]
        result = BridgeActivityAnalyzer.analyze_bridge_amounts(transactions)
        assert result["large_bridges_detected"] is False
        assert result["confidence"] == 0

    def test_detect_wash_bridging(self):
        transactions = [
            {"source_chain": "ethereum", "dest_chain": "polygon"},
            {"source_chain": "ethereum", "dest_chain": "polygon"},
            {"source_chain": "polygon", "dest_chain": "ethereum"},
            {"source_chain": "polygon", "dest_chain": "ethereum"},
        ]
        result = BridgeActivityAnalyzer.detect_wash_bridging(transactions)
        assert result["wash_bridging_detected"] is True
        assert result["confidence"] == 80

    def test_detect_wash_bridging_insufficient(self):
        transactions = [
            {"source_chain": "ethereum", "dest_chain": "polygon"},
            {"source_chain": "polygon", "dest_chain": "avalanche"},
        ]
        result = BridgeActivityAnalyzer.detect_wash_bridging(transactions)
        assert result["wash_bridging_detected"] is False

    def test_detect_wash_bridging_no_reverses(self):
        transactions = [
            {"source_chain": "ethereum", "dest_chain": "polygon"},
            {"source_chain": "ethereum", "dest_chain": "arbitrum"},
            {"source_chain": "polygon", "dest_chain": "optimism"},
            {"source_chain": "arbitrum", "dest_chain": "avalanche"},
        ]
        result = BridgeActivityAnalyzer.detect_wash_bridging(transactions)
        assert result["wash_bridging_detected"] is False


class TestBridgeContractAddresses:
    def test_multichain_addresses_defined(self):
        assert "multichain_anywap" in BRIDGE_CONTRACTS
        assert len(BRIDGE_CONTRACTS["multichain_anywap"]) >= 1

    def test_stargate_addresses_defined(self):
        assert "stargate" in BRIDGE_CONTRACTS
        assert len(BRIDGE_CONTRACTS["stargate"]) >= 1

    def test_layerzero_addresses_defined(self):
        assert "layerzero" in BRIDGE_CONTRACTS
        assert len(BRIDGE_CONTRACTS["layerzero"]) >= 1

    def test_wormhole_addresses_defined(self):
        assert "wormhole" in BRIDGE_CONTRACTS
        assert len(BRIDGE_CONTRACTS["wormhole"]) >= 1

    def test_polygon_bridge_addresses_defined(self):
        assert "polygon_bridge" in BRIDGE_CONTRACTS
        assert len(BRIDGE_CONTRACTS["polygon_bridge"]) >= 1
