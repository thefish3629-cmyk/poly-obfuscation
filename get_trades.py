import requests
import json

# Try to get market data from the CLOB API
url = 'https://clob.polymarket.com/markets'
response = requests.get(url)
print(f'CLOB status: {response.status_code}')

# Try the data API for this market
print('\n--- Trying Data API ---')
data_url = 'https://data-api.polymarket.com/trades'
params = {'market': '24906', 'limit': 100}
r = requests.get(data_url, params=params)
print(f'Data API status: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print(f'Trades: {len(data) if isinstance(data, list) else \"not list\"}')
    if isinstance(data, list) and data:
        print(f'Sample: {data[0]}')

# Try condition ID format
print('\n--- Trying condition ID from market 24906 ---')
# The condition ID is likely a hash of the question
# Let me try getting all recent trades and filter
trades_url = 'https://data-api.polymarket.com/trades'
r2 = requests.get(trades_url, params={'limit': 10})
print(f'All trades: {r2.status_code}')
if r2.status_code == 200:
    print(r2.text[:500])
