import requests

# Get all markets and search for nuclear-related ones
url = 'https://gamma-api.polymarket.com/markets'
params = {'closed': 'true', 'limit': 500}
response = requests.get(url, params=params)

if response.status_code == 200:
    markets = response.json()
    print(f'Total closed markets: {len(markets)}')
    
    # Search for nuclear/iran/israel
    for m in markets:
        q = m.get('question', '').lower()
        if 'nuclear' in q or ('iran' in q and 'israel' in q):
            print(f'\nQuestion: {m.get("question")}')
            print(f'Condition ID: {m.get("conditionId")}')
            print(f'Volume: ${float(m.get("volume", 0)):,.2f}')
            print(f'Closed: {m.get("closed")}')

# Also search specifically
print('\n\n=== Specific search ===')
params2 = {'question': 'nuclear facility', 'closed': 'true'}
response2 = requests.get(url, params=params2)
if response2.status_code == 200:
    for m in response2.json():
        print(f'{m.get("question")}')
