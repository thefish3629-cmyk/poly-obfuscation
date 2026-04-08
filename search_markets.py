import requests
import json

# Search for Iran-related markets
url = 'https://gamma-api.polymarket.com/markets'
params = {'question': 'iran', 'limit': 20}
response = requests.get(url, params=params)
print('Search by "iran":', response.status_code)
if response.status_code == 200:
    markets = response.json()
    print(f'Found {len(markets)} markets')
    for m in markets[:10]:
        q = m.get('question', 'N/A')[:70]
        cid = m.get('conditionId', 'N/A')
        print(f'  [{cid[:20]}...] {q}')

# Also try searching via public search
print('\n--- Public Search ---')
url2 = 'https://gamma-api.polymarket.com/public-search'
params2 = {'query': 'iran nuclear', 'limit': 10}
response2 = requests.get(url2, params=params2)
print('Search result:', response2.status_code)
if response2.status_code == 200:
    data = response2.json()
    print('Keys:', data.keys())
    print(json.dumps(data, indent=2)[:1000])
