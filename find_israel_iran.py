import requests

# Search for the specific market
url = 'https://gamma-api.polymarket.com/markets'
params = {'question': 'Israel strike on Iranian nuclear facility before July', 'closed': 'true', 'limit': 10}
r = requests.get(url, params=params)
print(f'Search status: {r.status_code}')

if r.status_code == 200:
    data = r.json()
    print(f'Found: {len(data)} markets')
    for m in data:
        print(f'\nQuestion: {m.get("question")}')
        print(f'Condition ID: {m.get("conditionId")}')
        print(f'Slug: {m.get("slug")}')
        print(f'Volume: ${float(m.get("volume", 0)):,.2f}')
        print(f'Closed: {m.get("closed")}')

# Also try with just parts
print('\n--- Alternative search ---')
params2 = {'question': 'Iran nuclear facility July', 'closed': 'true'}
r2 = requests.get(url, params=params2)
if r2.status_code == 200:
    for m in r2.json()[:3]:
        print(f'{m.get("question")} - {m.get("conditionId")}')
