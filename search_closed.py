import requests

url = 'https://gamma-api.polymarket.com/markets'
params = {'closed': 'true', 'limit': 200}
response = requests.get(url, params=params)

if response.status_code == 200:
    markets = response.json()
    
    # Filter for Iran-related
    iran_markets = []
    for m in markets:
        q = m.get('question', '').lower()
        if 'iran' in q or 'israel' in q or 'nuclear' in q:
            iran_markets.append(m)
    
    print(f'Total Iran/Israel/Nuclear markets: {len(iran_markets)}')
    for m in iran_markets[:10]:
        q = m.get('question', 'N/A')
        cid = m.get('conditionId', 'N/A')
        vol = m.get('volume', 'N/A')
        closed = m.get('closed', False)
        print(f'  [{cid}]')
        print(f'    {q}')
        print(f'    Volume: ${float(vol):,.2f}, Closed: {closed}')
        print()
