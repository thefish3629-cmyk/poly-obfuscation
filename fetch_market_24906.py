import requests

# Fetch the specific market
url = 'https://gamma-api.polymarket.com/markets/24906'
response = requests.get(url)
print(f'Status: {response.status_code}')

if response.status_code == 200:
    market = response.json()
    print(f'\nQuestion: {market.get("question")}')
    print(f'Condition ID: {market.get("conditionId")}')
    print(f'Slug: {market.get("slug")}')
    print(f'Volume: ${float(market.get("volume", 0)):,.2f}')
    print(f'Closed: {market.get("closed")}')
    print(f'End Date: {market.get("endDate")}')
    print(f'Tokens: {market.get("clobTokenIds")}')

# Try searching by slug pattern
print('\n--- Trying slug ---')
slug = 'will-israel-strike-an-iranian-nuclear-facility-before-july-2025'
url2 = 'https://gamma-api.polymarket.com/markets'
params = {'slug': slug}
response2 = requests.get(url2, params=params)
print(f'Search by slug: {response2.status_code}')
if response2.status_code == 200:
    data = response2.json()
    if data:
        m = data[0]
        print(f'\nQuestion: {m.get("question")}')
        print(f'Condition ID: {m.get("conditionId")}')
        print(f'Volume: ${float(m.get("volume", 0)):,.2f}')
