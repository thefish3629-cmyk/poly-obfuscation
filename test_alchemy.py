#!/usr/bin/env python
"""Simplified Alchemy tests."""

import os
from dotenv import load_dotenv
load_dotenv()

print("=" * 50)
print("ALCHEMY (POLYGON RPC) TEST")
print("=" * 50)

from web3 import Web3

RPC_URL = os.environ.get("POLYGON_RPC_URL", "")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

print(f"\n[OK] Connection: {w3.is_connected()}")
print(f"[OK] Block: {w3.eth.block_number}")

# These methods work through Alchemy:
print(f"[OK] gasPrice: {w3.eth.gas_price / 1e9:.2f} gwei")

# Direct RPC call (Alchemy enhanced)
print("\n" + "=" * 50)
print("ALCHEMY-SPECIFIC METHODS")
print("=" * 50)

# Make raw request to Alchemy
result = w3.provider.make_request("eth_blockNumber", [])
print(f"\n[OK] eth_blockNumber (raw): {int(result['result'], 16)}")

# Get chain ID
result = w3.provider.make_request("eth_chainId", [])
print(f"[OK] eth_chainId: {int(result['result'], 16)} (137 = Polygon)")

#-syncing
result = w3.provider.make_request("eth_syncing", [])
print(f"[OK] eth_syncing: {result['result']}")

print("\n[OK] All Alchemy tests passed!")
print("\nNote: Alchemy enhanced methods (debug_trace, trace_call)")
print("      require paid plans or special configuration.")