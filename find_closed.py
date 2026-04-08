import requests
import json

url = 'https://gamma-api.polymarket.com/markets'
params = {'closed': 'true', 'limit': 50}
response = requests.get(url, params=params)

if response.status_code == 200:
    markets = response.json()
    print(f'Found {len(markets)} closed markets')
    
    # Show top volume closed markets
    sorted_markets = sorted(markets, key=lambda x: float(x.get('volume', 0) or 0), reverse=True)
    print('\n=== Top Volume Closed Markets ===')
    for m in sorted_markets[:15]:
        q = m.get('question', 'N/A')[:70]
        vol = float(m.get('volume', 0) or 0)
        cid = m.get('conditionId', 'N/A')
        print(f'${vol:>15,.2f} - {q}')
        print(f'   ID: {cid[:40]}...')
