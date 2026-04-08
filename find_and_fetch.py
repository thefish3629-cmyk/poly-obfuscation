import requests
import json

print("=" * 70)
print("FETCHING REAL TRADES FROM POLYMARKET DATA API")
print("=" * 70)

# 1. Fetch recent trades from the Data API
print("\n[1/3] Fetching recent trades...")
trades_url = 'https://data-api.polymarket.com/trades'
r = requests.get(trades_url, params={'limit': 100}, timeout=30)

if r.status_code == 200:
    trades = r.json()
    print(f"  Got {len(trades)} trades")
    
    if trades:
        print("\n  Sample trade:")
        print(json.dumps(trades[0], indent=2))
        
        # Get unique markets (conditionIds)
        condition_ids = set(t.get('conditionId') for t in trades if t.get('conditionId'))
        print(f"\n  Unique markets: {len(condition_ids)}")
        for cid in list(condition_ids)[:5]:
            print(f"    - {cid}")

# 2. Search for Iran/Israel/Nuclear markets
print("\n[2/3] Searching for Iran nuclear market...")

# Try Gamma API with various searches
searches = [
    {'question': 'Iran nuclear', 'closed': 'false'},
    {'question': 'Israel Iran', 'closed': 'false'},
    {'question': 'Iran nuclear', 'closed': 'true'},
    {'slug': 'iran-nuclear'},
    {'slug': 'israel-strike'},
]

for params in searches:
    url = 'https://gamma-api.polymarket.com/markets'
    r = requests.get(url, params=params, timeout=10)
    if r.status_code == 200 and r.json():
        markets = r.json()
        print(f"\n  Search {params}: Found {len(markets)}")
        for m in markets[:3]:
            print(f"    - {m.get('question')[:60]} ({m.get('conditionId')[:20]}...)")

# 3. Try fetching market by condition ID prefix
print("\n[3/3] Checking if Iran nuclear market exists by condition ID...")

# The condition ID for Israel-Iran nuclear likely starts with a hash
# Let's check if there's a market that matches our target
target_patterns = ['iran', 'nuclear', 'israel', 'iranian']

gamma_url = 'https://gamma-api.polymarket.com/markets'
params = {'closed': 'false', 'limit': 200}
r = requests.get(gamma_url, params=params, timeout=10)

if r.status_code == 200:
    all_markets = r.json()
    print(f"  Total active markets: {len(all_markets)}")
    
    # Search for nuclear/geopolitical
    nuclear_markets = []
    for m in all_markets:
        q = m.get('question', '').lower()
        if 'nuclear' in q or ('iran' in q and 'attack' in q) or ('iran' in q and 'strike' in q) or ('iran' in q and 'israel' in q):
            nuclear_markets.append(m)
    
    print(f"\n  Nuclear/Geopolitical markets: {len(nuclear_markets)}")
    for m in nuclear_markets:
        print(f"    - {m.get('question')}")
        print(f"      ID: {m.get('conditionId')}")
        print(f"      Volume: ${float(m.get('volume', 0)):,.2f}")

# 4. Use the highest volume Iran-related market
print("\n[4/3] Using highest volume Iran market...")
params = {'question': 'Iran', 'closed': 'false'}
r = requests.get(gamma_url, params=params, timeout=10)
if r.status_code == 200:
    iran_markets = [m for m in r.json() if float(m.get('volume', 0)) > 10000]
    if iran_markets:
        # Sort by volume
        iran_markets.sort(key=lambda x: float(x.get('volume', 0)), reverse=True)
        best = iran_markets[0]
        print(f"  Market: {best.get('question')}")
        print(f"  Condition ID: {best.get('conditionId')}")
        print(f"  Volume: ${float(best.get('volume', 0)):,.2f}")

print("\n" + "=" * 70)
