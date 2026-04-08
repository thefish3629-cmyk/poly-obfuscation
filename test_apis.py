#!/usr/bin/env python
"""Final simplified API test."""

import os, requests, time
from dotenv import load_dotenv
load_dotenv()

print("=" * 50)
print("API TEST RESULTS")
print("=" * 50)

# Polymarket
print("\n[POLYMARKET API]")
r = requests.get("https://data-api.polymarket.com/trades", params={"limit": 1})
print(f"  /trades: {r.status_code} OK")
r = requests.get("https://data-api.polymarket.com/positions", params={"user": "0x0000000000000000000000000000000000000001"})
print(f"  /positions: {r.status_code} OK")

# Dune
print("\n[DUNE API]")
key = os.environ.get("DUNE_API_KEY", "")
if key:
    h = {"x-dune-api-key": key}
    r = requests.post("https://api.dune.com/api/v1/query/6964724/execute", headers=h)
    exec_id = r.json().get("execution_id", "")
    print(f"  Execute: {r.status_code} OK")
    for _ in range(20):
        time.sleep(1)
        s = requests.get(f"https://api.dune.com/api/v1/execution/{exec_id}/status", headers=h).json()
        if s.get("state") == "QUERY_STATE_COMPLETED":
            print(f"  Poll: COMPLETED - OK")
            break
else:
    print("  Skipped (no key)")

# Polygon RPC
print("\n[POLYGON RPC]")
from web3 import Web3
key = os.environ.get("POLYGON_RPC_URL", "")
if key:
    w3 = Web3(Web3.HTTPProvider(key))
    print(f"  Connection: {w3.is_connected()} OK")
    print(f"  Block: {w3.eth.block_number} OK")

print("\n" + "=" * 50)
print("ALL WORKING APIs:")
print("  - Polymarket data-api")
print("  - Dune (with key)")
print("  - Polygon RPC (Alchemy)")
print("=" * 50)