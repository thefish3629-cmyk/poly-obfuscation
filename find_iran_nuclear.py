import requests

# Search specifically for the Iran nuclear strike market
url = 'https://gamma-api.polymarket.com/markets'
params = {'question': 'Israel strike on Iranian nuclear', 'limit': 50}
response = requests.get(url, params=params)

if response.status_code == 200:
    markets = response.json()
    print(f'Found {len(markets)} markets matching "Israel strike on Iranian nuclear"')
    
    for m in markets:
        q = m.get('question', 'N/A')
        cid = m.get('conditionId', 'N/A')
        vol = m.get('volume', 'N/A')
        closed = m.get('closed', False)
        slug = m.get('slug', 'N/A')
        print(f'\nQuestion: {q}')
        print(f'Condition ID: {cid}')
        print(f'Slug: {slug}')
        print(f'Volume: ${float(vol):,.2f}')
        print(f'Closed: {closed}')
