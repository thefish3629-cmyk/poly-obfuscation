import requests
import time
from datetime import datetime

print("=" * 70)
print("FETCHING REAL POLYMARKET DATA - FIXED")
print("=" * 70)

# 1. Find the Iran nuclear market
print("\n[1/4] Finding Iran nuclear market...")

url = 'https://gamma-api.polymarket.com/markets'

# Search broadly
params = {'closed': 'true', 'limit': 500}
r = requests.get(url, params=params)
print(f"  Fetched {len(r.json())} closed markets")

iran_markets = []
for m in r.json():
    q = m.get('question', '').lower()
    if 'iran' in q and ('nuclear' in q or 'facility' in q or 'july' in q):
        iran_markets.append(m)
        print(f"  Match: {m.get('question')[:60]}...")

# Also search by question keyword
params2 = {'question': 'Iran', 'closed': 'true'}
r2 = requests.get(url, params=params2)
for m in r2.json():
    if m not in iran_markets:
        q = m.get('question', '').lower()
        if 'nuclear' in q:
            iran_markets.append(m)
            print(f"  Found: {m.get('question')[:60]}...")

if iran_markets:
    market = iran_markets[0]
    CONDITION_ID = market.get('conditionId')
    QUESTION = market.get('question')
    print(f"\n  Using: {QUESTION}")
else:
    print("\n  No Iran nuclear market found in API.")
    print("  The market may have been deleted or never existed.")
    print("  Let's check for Israel-related markets...")
    
    israel_markets = []
    for m in r.json():
        q = m.get('question', '').lower()
        if 'israel' in q:
            israel_markets.append(m)
    
    if israel_markets:
        print(f"  Found {len(israel_markets)} Israel markets:")
        for m in israel_markets[:5]:
            print(f"    - {m.get('question')[:60]}...")

# 2. Try Goldsky with correct query
print("\n[2/4] Fetching from Goldsky subgraphs...")

GOLDSKY_BASE = "https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs"

# Try orderbook subgraph with correct field names
query_orderbook = """
{
    orderFills(first: 100, orderBy: timestamp, orderDirection: desc) {
        id
        transactionHash
        blockNumber
        timestamp
        maker
        taker
        makerAmountFilled
        takerAmountFilled
        conditionId
    }
}
"""

# Try positions subgraph
query_positions = """
{
    userBalances(first: 100) {
        id
        user
        balance
        netBalance
    }
}
"""

# Try activity subgraph
query_activity = """
{
    splits(first: 100) {
        id
        user
        collateralAmount
        timestamp
    }
}
"""

subgraphs_to_try = [
    ("orderbook", query_orderbook),
    ("positions", query_positions),
    ("activity", query_activity),
]

for name, query in subgraphs_to_try:
    subgraph_url = f"{GOLDSKY_BASE}/{name}-subgraph/0.0.1/gn"
    print(f"\n  Trying {name} subgraph...")
    try:
        r = requests.post(subgraph_url, json={'query': query}, timeout=30)
        if r.status_code == 200:
            data = r.json()
            if 'data' in data and data['data']:
                keys = list(data['data'].keys())
                print(f"    Fields available: {keys}")
                first_item = data['data'].get(keys[0], [])[0] if keys else {}
                if first_item:
                    print(f"    Sample: {first_item}")
            else:
                print(f"    No data: {data}")
        else:
            print(f"    Error {r.status_code}: {r.text[:100]}")
    except Exception as e:
        print(f"    Exception: {e}")

# 3. Try Dune Analytics - list queries
print("\n[3/4] Checking Dune Analytics...")

DUNE_KEY = "XRdFWOXj9uJf7fY7EABjrfFxwhsw26DL"
headers = {"x-dune-api-key": DUNE_KEY}

# Try to list user's queries
try:
    r = requests.get("https://api.dune.com/api/v1/query", headers=headers, timeout=10)
    print(f"  Dune query list: {r.status_code}")
    if r.status_code == 200:
        queries = r.json().get('result', [])
        print(f"  Found {len(queries)} queries")
        for q in queries[:5]:
            print(f"    - ID: {q.get('id')} | {q.get('name', 'N/A')}")
    else:
        print(f"  Error: {r.text[:200]}")
except Exception as e:
    print(f"  Exception: {e}")

# 4. Try the Polymarket data API directly
print("\n[4/4] Trying Polymarket Data API...")

data_urls = [
    'https://data-api.polymarket.com/trades',
    'https://data-api.polymarket.com/positions',
]

for data_url in data_urls:
    print(f"  Trying {data_url}...")
    try:
        r = requests.get(data_url, timeout=10)
        print(f"    Status: {r.status_code}")
        if r.status_code == 200:
            print(f"    Response: {r.text[:200]}")
        else:
            print(f"    Error: {r.text[:200]}")
    except Exception as e:
        print(f"    Exception: {e}")

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
