import requests

# Search with variations
search_terms = ['iranian nuclear', 'israel strike', 'iran nuclear', 'nuclear facility', 'iranian nuclear facility']
for term in search_terms:
    url = 'https://gamma-api.polymarket.com/markets'
    params = {'question': term, 'closed': 'true', 'limit': 10}
    r = requests.get(url, params=params)
    if r.status_code == 200:
        data = r.json()
        if data:
            print(f'Search "{term}": Found {len(data)}')
            for m in data:
                q = m.get('question', '')
                if 'nuclear' in q.lower():
                    print(f'  FOUND: {q}')
                    print(f'  ID: {m.get("conditionId")}')
                    print(f'  Volume: ${float(m.get("volume", 0)):,.2f}')
                    print(f'  Closed: {m.get("closed")}')
