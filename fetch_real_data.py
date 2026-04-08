import requests
import time

print("=" * 70)
print("FETCHING REAL POLYMARKET DATA")
print("=" * 70)

# First, search for the Israel-Iran nuclear market
print("\n[1/3] Finding the Israel-Iran nuclear market...")

# Try multiple search approaches
search_results = []

# Approach 1: Direct API search
url = 'https://gamma-api.polymarket.com/markets'
params = {'question': 'Israel', 'closed': 'true', 'limit': 50}
r = requests.get(url, params=params)
if r.status_code == 200:
    for m in r.json():
        q = m.get('question', '').lower()
        if 'iran' in q or 'nuclear' in q:
            search_results.append(m)
            print(f"  Found: {m.get('question')}")

# Approach 2: Try slug pattern
slugs_to_try = [
    'will-israel-strike-an-iranian-nuclear-facility-before-july',
    'israel-strike-iran-nuclear',
    'iran-nuclear-facility-july',
]

for slug in slugs_to_try:
    params = {'slug': slug}
    r = requests.get(url, params=params)
    if r.status_code == 200 and r.json():
        m = r.json()[0]
        if m not in search_results:
            search_results.append(m)
            print(f"  Found via slug: {m.get('question')}")

# Approach 3: Get all closed markets and filter
if not search_results:
    print("  Searching all closed markets...")
    params = {'closed': 'true', 'limit': 500}
    r = requests.get(url, params=params)
    if r.status_code == 200:
        for m in r.json():
            q = m.get('question', '').lower()
            if 'nuclear' in q:
                search_results.append(m)
                print(f"  Found: {m.get('question')[:70]}")

print(f"\nTotal Iran/Nuclear markets found: {len(search_results)}")

if search_results:
    # Use the first one
    market = search_results[0]
    CONDITION_ID = market.get('conditionId')
    QUESTION = market.get('question')
    print(f"\nUsing market: {QUESTION}")
    print(f"Condition ID: {CONDITION_ID}")
else:
    print("\nNo Iran-Nuclear market found. Let's try the Goldsky subgraph directly...")
    CONDITION_ID = None
    QUESTION = None

# Try Goldsky subgraph for trades
print("\n[2/3] Fetching trades from Goldsky subgraph...")

# Goldsky has public Polymarket subgraphs
GOLDSKY_URL = "https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs"

subgraphs = [
    ("orderbook", "/orderbook-subgraph/0.0.1/gn"),
    ("positions", "/positions-subgraph/0.0.7/gn"),
]

query = """
{
    orderFilleds(first: 100, orderBy: timestamp, orderDirection: desc) {
        id
        transactionHash
        blockNumber
        timestamp
        maker
        taker
        makerAmountFilled
        takerAmountFilled
        conditionId
        makerAssetId
        takerAssetId
    }
}
"""

all_trades = []

for name, path in subgraphs:
    full_url = GOLDSKY_URL + path
    print(f"  Trying {name} subgraph...")
    try:
        r = requests.post(full_url, json={'query': query}, timeout=30)
        if r.status_code == 200:
            data = r.json()
            if 'data' in data and data['data']:
                trades = data['data'].get('orderFilleds', [])
                print(f"    Found {len(trades)} trades!")
                if trades:
                    all_trades.extend(trades)
                    print(f"    Sample: {trades[0]}")
                    break
        else:
            print(f"    Error: {r.status_code} - {r.text[:200]}")
    except Exception as e:
        print(f"    Exception: {e}")

print(f"\nTotal trades from Goldsky: {len(all_trades)}")

# Try Dune Analytics
print("\n[3/3] Trying Dune Analytics...")

# Dune has public queries for Polymarket
# Let's try to run a query
DUNE_API_KEY = "XRdFWOXj9uJf7fY7EABjrfFxwhsw26DL"

if DUNE_API_KEY:
    # List available queries
    headers = {"x-dune-api-key": DUNE_API_KEY}
    
    # Try executing the Polymarket trades query
    query_url = f"https://api.dune.com/api/v1/query/2435483/execute"
    payload = {
        "parameters": [
            {"name": "days", "type": "number", "value": 365},
            {"name": "limit", "type": "number", "value": 1000}
        ]
    }
    
    try:
        r = requests.post(query_url, json=payload, headers=headers, timeout=10)
        print(f"  Dune query response: {r.status_code}")
        if r.status_code == 200:
            result = r.json()
            exec_id = result.get('execution_id')
            print(f"  Execution ID: {exec_id}")
            
            # Wait for results
            if exec_id:
                print("  Waiting for results...")
                for i in range(10):
                    time.sleep(5)
                    status_url = f"https://api.dune.com/api/v1/execution/{exec_id}/status"
                    sr = requests.get(status_url, headers=headers)
                    state = sr.json().get('state')
                    print(f"    Status: {state}")
                    if state == 'QUERY_STATE_COMPLETED':
                        results_url = f"https://api.dune.com/api/v1/execution/{exec_id}/results"
                        rr = requests.get(results_url, headers=headers)
                        rows = rr.json().get('result', {}).get('rows', [])
                        print(f"    Got {len(rows)} rows!")
                        break
                    elif state == 'QUERY_STATE_FAILED':
                        break
        else:
            print(f"  Error: {r.text[:300]}")
    except Exception as e:
        print(f"  Exception: {e}")

print("\n" + "=" * 70)
print("DATA FETCH COMPLETE")
print("=" * 70)
