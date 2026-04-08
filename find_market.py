import requests
import json

# Get all Iran-specific markets
url = 'https://gamma-api.polymarket.com/markets'
params = {'closed': 'false', 'limit': 100}
response = requests.get(url, params=params)

if response.status_code == 200:
    markets = response.json()
    
    # Filter for Iran-related
    iran_markets = []
    for m in markets:
        q = m.get('question', '').lower()
        if 'iran' in q or 'israel' in q:
            iran_markets.append(m)
    
    print(f'Total Iran/Israel markets: {len(iran_markets)}')
    for m in iran_markets:
        q = m.get('question', 'N/A')
        cid = m.get('conditionId', 'N/A')
        vol = m.get('volume', 'N/A')
        print(f'  [{cid}]')
        print(f'    {q}')
        print(f'    Volume: ${float(vol):,.2f}' if vol else '    Volume: N/A')
        print()
    
    # Also show top volume markets
    print('\n=== Top Volume Markets ===')
    sorted_markets = sorted(markets, key=lambda x: float(x.get('volume', 0) or 0), reverse=True)
    for m in sorted_markets[:5]:
        q = m.get('question', 'N/A')[:60]
        vol = float(m.get('volume', 0) or 0)
        print(f'  ${vol:>15,.2f} - {q}')
