import pytest
from datetime import datetime
from unittest.mock import MagicMock

from src.detection.layering import LayeringDetector


class TestLayeringDetector:
    def test_init(self, mock_postgres_store, mock_onchain_client):
        detector = LayeringDetector(mock_postgres_store, mock_onchain_client)
        assert detector.store == mock_postgres_store
        assert detector.onchain == mock_onchain_client
        assert detector.FAN_OUT_THRESHOLD == 5
        assert detector.FAN_IN_THRESHOLD == 5
        assert detector.HOP_THRESHOLD == 3

    def test_detect_for_wallet_no_hops(self, mock_postgres_store, mock_onchain_client, sample_wallet_address):
        mock_onchain_client.trace_fund_origin.return_value = []
        
        detector = LayeringDetector(mock_postgres_store, mock_onchain_client)
        flags = detector.detect_for_wallet(sample_wallet_address)
        
        assert len(flags) == 0

    def test_detect_for_wallet_fan_pattern(
        self, mock_postgres_store, mock_onchain_client, sample_wallet_address
    ):
        hops = [
            {
                "from_address": f"0x{i:039x}0000000000000000000000000000000000000001",
                "to_address": sample_wallet_address,
                "amount": "100.0",
                "contract_type": "wallet",
                "hop_number": 1
            }
            for i in range(6)
        ]
        mock_onchain_client.trace_fund_origin.return_value = hops
        
        detector = LayeringDetector(mock_postgres_store, mock_onchain_client)
        flags = detector.detect_for_wallet(sample_wallet_address)
        
        fan_flags = [f for f in flags if f.flag_type == "layering_fan_pattern"]
        assert len(fan_flags) == 1

    def test_detect_for_wallet_circular_flow(
        self, mock_postgres_store, mock_onchain_client, sample_wallet_address
    ):
        hops = [
            {
                "from_address": "0x1111111111111111111111111111111111111111",
                "to_address": "0x2222222222222222222222222222222222222222",
                "amount": "100.0",
                "contract_type": "wallet"
            },
            {
                "from_address": "0x2222222222222222222222222222222222222222",
                "to_address": "0x1111111111111111111111111111111111111111",
                "amount": "100.0",
                "contract_type": "wallet"
            }
        ]
        mock_onchain_client.trace_fund_origin.return_value = hops
        
        detector = LayeringDetector(mock_postgres_store, mock_onchain_client)
        flags = detector.detect_for_wallet(sample_wallet_address)
        
        circular_flags = [f for f in flags if f.flag_type == "layering_circular"]
        assert len(circular_flags) == 1
        assert circular_flags[0].confidence == 80.0

    def test_detect_for_wallet_multi_hop(
        self, mock_postgres_store, mock_onchain_client, sample_wallet_address
    ):
        hops = [
            {
                "from_address": "0x1111111111111111111111111111111111111111",
                "to_address": sample_wallet_address,
                "amount": "100.0",
                "contract_type": "wallet",
                "hop_number": 1
            },
            {
                "from_address": "0x2222222222222222222222222222222222222222",
                "to_address": sample_wallet_address,
                "amount": "100.0",
                "contract_type": "wallet",
                "hop_number": 3
            },
            {
                "from_address": "0x3333333333333333333333333333333333333333",
                "to_address": sample_wallet_address,
                "amount": "100.0",
                "contract_type": "wallet",
                "hop_number": 4
            }
        ]
        mock_onchain_client.trace_fund_origin.return_value = hops
        
        detector = LayeringDetector(mock_postgres_store, mock_onchain_client)
        flags = detector.detect_for_wallet(sample_wallet_address)
        
        multi_hop_flags = [f for f in flags if f.flag_type == "layering_multi_hop"]
        assert len(multi_hop_flags) == 1
        assert multi_hop_flags[0].confidence == 65.0

    def test_analyze_fan_patterns_fan_out(self, mock_postgres_store, mock_onchain_client, sample_wallet_address):
        hops = [
            {
                "from_address": sample_wallet_address,
                "to_address": f"0x{i:039x}" + "0" * 1,
                "amount": "100.0",
                "contract_type": "wallet"
            }
            for i in range(6)
        ]
        
        detector = LayeringDetector(mock_postgres_store, mock_onchain_client)
        result = detector._analyze_fan_patterns(hops, sample_wallet_address)
        
        assert result["detected"] is True
        assert result["details"]["fan_out_wallets"] >= 5

    def test_analyze_fan_patterns_fan_in(self, mock_postgres_store, mock_onchain_client, sample_wallet_address):
        hops = [
            {
                "from_address": f"0x{i:039x}" + "0" * 1,
                "to_address": sample_wallet_address,
                "amount": "100.0",
                "contract_type": "wallet"
            }
            for i in range(6)
        ]
        
        detector = LayeringDetector(mock_postgres_store, mock_onchain_client)
        result = detector._analyze_fan_patterns(hops, sample_wallet_address)
        
        assert result["detected"] is True
        assert result["details"]["fan_in_wallets"] >= 5

    def test_analyze_fan_patterns_no_detection(self, mock_postgres_store, mock_onchain_client, sample_wallet_address):
        hops = [
            {
                "from_address": "0x1111111111111111111111111111111111111111",
                "to_address": sample_wallet_address,
                "amount": "100.0",
                "contract_type": "wallet"
            },
            {
                "from_address": "0x2222222222222222222222222222222222222222",
                "to_address": sample_wallet_address,
                "amount": "100.0",
                "contract_type": "wallet"
            }
        ]
        
        detector = LayeringDetector(mock_postgres_store, mock_onchain_client)
        result = detector._analyze_fan_patterns(hops, sample_wallet_address)
        
        assert result["detected"] is False

    def test_detect_circular_flows_detected(self, mock_postgres_store, mock_onchain_client):
        hops = [
            {"from_address": "A", "to_address": "B"},
            {"from_address": "B", "to_address": "A"},
        ]
        
        detector = LayeringDetector(mock_postgres_store, mock_onchain_client)
        result = detector._detect_circular_flows(hops, "A")
        
        assert result["detected"] is True
        assert result["details"]["circular_paths_found"] > 0

    def test_detect_circular_flows_no_detection(self, mock_postgres_store, mock_onchain_client):
        hops = [
            {"from_address": "A", "to_address": "B"},
            {"from_address": "B", "to_address": "C"},
            {"from_address": "D", "to_address": "E"},
        ]
        
        detector = LayeringDetector(mock_postgres_store, mock_onchain_client)
        result = detector._detect_circular_flows(hops, "A")
        
        assert result["detected"] is False

    def test_analyze_multi_hop_patterns_excessive_hops(self, mock_postgres_store, mock_onchain_client, sample_wallet_address):
        hops = [
            {"from_address": "0x1111", "to_address": sample_wallet_address, "hop_number": i, "amount": "100.0"}
            for i in range(1, 5)
        ]
        
        detector = LayeringDetector(mock_postgres_store, mock_onchain_client)
        result = detector._analyze_multi_hop_patterns(hops, sample_wallet_address)
        
        assert result["detected"] is True
        assert result["details"]["max_hops"] >= 3

    def test_analyze_multi_hop_patterns_normal(self, mock_postgres_store, mock_onchain_client, sample_wallet_address):
        hops = [
            {"from_address": "0x1111", "to_address": sample_wallet_address, "hop_number": 1, "amount": "100.0"},
            {"from_address": "0x2222", "to_address": sample_wallet_address, "hop_number": 2, "amount": "100.0"},
        ]
        
        detector = LayeringDetector(mock_postgres_store, mock_onchain_client)
        result = detector._analyze_multi_hop_patterns(hops, sample_wallet_address)
        
        assert result["detected"] is False

    def test_build_fund_flow_graph(self, mock_postgres_store, mock_onchain_client, sample_wallet_address):
        mock_onchain_client.trace_fund_origin.return_value = [
            {
                "from_address": "0x1111",
                "to_address": sample_wallet_address,
                "token": "USDC",
                "amount": "100.0",
                "contract_type": "wallet"
            }
        ]
        
        detector = LayeringDetector(mock_postgres_store, mock_onchain_client)
        graph = detector.build_fund_flow_graph([sample_wallet_address])
        
        assert graph.number_of_nodes() > 0

    def test_find_reconsolidation_points(self, mock_postgres_store, mock_onchain_client, sample_wallet_address):
        mock_onchain_client.trace_fund_origin.return_value = [
            {
                "from_address": f"0x{i:039x}" + "0" * 1,
                "to_address": sample_wallet_address,
                "amount": "100.0"
            }
            for i in range(3)
        ] + [
            {
                "from_address": "0x1111111111111111111111111111111111111111",
                "to_address": sample_wallet_address,
                "amount": "50.0"
            }
        ]
        
        detector = LayeringDetector(mock_postgres_store, mock_onchain_client)
        points = detector.find_reconsolidation_points(sample_wallet_address)
        
        assert isinstance(points, list)

    def test_run_detection(self, mock_postgres_store, mock_onchain_client, sample_wallet_address):
        mock_onchain_client.trace_fund_origin.return_value = []
        
        detector = LayeringDetector(mock_postgres_store, mock_onchain_client)
        total_flags = detector.run_detection(addresses=[sample_wallet_address])
        
        assert total_flags == 0


class TestLayeringThresholds:
    def test_threshold_defaults(self, mock_postgres_store, mock_onchain_client):
        detector = LayeringDetector(mock_postgres_store, mock_onchain_client)
        
        assert detector.FAN_OUT_THRESHOLD == 5
        assert detector.FAN_IN_THRESHOLD == 5
        assert detector.HOP_THRESHOLD == 3
        assert detector.CIRCULAR_THRESHOLD == 0.3
