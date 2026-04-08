import requests

url = 'https://gamma-api.polymarket.com/markets'
params = {'closed': 'false', 'limit': 20}
response = requests.get(url, params=params)
print('Status:', response.status_code)
if response.status_code == 200:
    markets = response.json()
    print(f'Found {len(markets)} markets')
    for m in markets[:10]:
        q = m.get('question', 'N/A')[:70]
        print(f'  - {q}')
else:
    print('Response:', response.text[:500])
