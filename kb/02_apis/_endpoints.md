# API Endpoints Quick Reference

Complete cheat sheet for all APIs used in this project.

---

## POLYMARKET API

### Markets

| Endpoint | Method | URL | Params |
|----------|--------|-----|--------|
| Search | GET | `https://gamma.polymarket.com/markets` | `question`, `limit` |
| By slug | GET | `https://gamma.polymarket.com/markets` | `slug` |
| By ID | GET | `https://gamma.polymarket.com/markets/{id}` | - |
| CLOB | GET | `https://clob.polymarket.com/markets` | `question` |
| Fallback | GET | `https://api.polymarket.com/markets` | `question` |

### Trades

| Endpoint | Method | URL | Params |
|----------|--------|-----|--------|
| By market | GET | `https://data-api.polymarket.com/trades` | `market`, `limit` |
| By user | GET | `https://data-api.polymarket.com/trades` | `user`, `limit` |

### User Data

| Endpoint | Method | URL | Params |
|----------|--------|-----|--------|
| Positions | GET | `https://data-api.polymarket.com/positions` | `user` |
| Activity | GET | `https://data-api.polymarket.com/activity` | `user` |

### Market Data

| Endpoint | Method | URL | Params |
|----------|--------|-----|--------|
| Order book | GET | `https://clob.polymarket.com/order-book/{token}` | - |
| Price history | GET | `https://clob.polymarket.com/prices-history` | `token_id`, `interval` |

---

## DUNE API

### Query Execution

| Endpoint | Method | URL |
|----------|--------|-----|
| Execute | POST | `https://api.dune.com/api/v1/query/{id}/execute` |
| Status | GET | `https://api.dune.com/api/v1/execution/{exec_id}/status` |
| Results | GET | `https://api.dune.com/api/v1/execution/{exec_id}/results` |
| List | GET | `https://api.dune.com/api/v1/query` |

### Header
```
x-dune-api-key: YOUR_KEY
```

### Execution States
- `QUERY_STATE_EXECUTING` - Running, wait
- `QUERY_STATE_FAILED` - Error
- `QUERY_STATE_COMPLETED` - Done

---

## GOLDSKY API

### Subgraphs

| Subgraph | URL |
|----------|-----|
| Orderbook | `https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/orderbook-subgraph/0.0.1/gn` |
| Positions | `https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/positions-subgraph/0.0.7/gn` |
| Activity | `https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/activity-subgraph/0.0.4/gn` |
| PnL | `https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/pnl-subgraph/0.0.14/gn` |

### Method
```
POST <subgraph_url>
Body: {"query": "...", "variables": {...}}
```

### Header
```
x-api-key: YOUR_KEY (optional for public)
```

---

## POLYGON RPC (ALCHEMY)

### Connection

```python
from web3 import Web3
w3 = Web3(Web3.HTTPProvider("https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY"))
```

### Key Methods

| Method | Web3 Call |
|--------|-----------|
| Latest block | `w3.eth.block_number` |
| Balance | `w3.eth.get_balance(addr)` |
| Nonce | `w3.eth.get_transaction_count(addr)` |
| Code | `w3.eth.get_code(addr)` |
| Receipt | `w3.eth.get_transaction_receipt(tx_hash)` |
| Logs | `w3.eth.get_logs(filter)` |
| Call | `w3.eth.call(tx)` |

### ERC-20 Balance

```python
contract.functions.balanceOf(wallet).call()
# Divide by 1e6 for USDC
# Divide by 1e18 for WMATIC
```

---

## CURL QUICK REFERENCE

### Polymarket Search
```bash
curl "https://gamma.polymarket.com/markets?question=iran&limit=5"
```

### Polymarket Trades
```bash
curl "https://data-api.polymarket.com/trades?market=0x123&limit=100"
```

### Dune Execute
```bash
curl -X POST "https://api.dune.com/api/v1/query/6964724/execute" \
  -H "x-dune-api-key: YOUR_KEY"
```

### Dune Status
```bash
curl "https://api.dune.com/api/v1/execution/EXEC_ID/status" \
  -H "x-dune-api-key: YOUR_KEY"
```

### Dune Results
```bash
curl "https://api.dune.com/api/v1/execution/EXEC_ID/results?limit=10000" \
  -H "x-dune-api-key: YOUR_KEY"
```

### Polygon Balance
```bash
curl -X POST "https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_getBalance","params":["ADDRESS","latest"],"id":1}'
```

---

## PYTHON QUICK REFERENCE

### Get Markets
```python
import requests
response = requests.get("https://gamma.polymarket.com/markets", params={"question": "iran"})
markets = response.json()
```

### Get Trades
```python
response = requests.get("https://data-api.polymarket.com/trades", params={"market": condition_id})
trades = response.json()
```

### Dune Query
```python
import requests, time
exec_resp = requests.post(f"{BASE}/query/6964724/execute", headers=headers)
exec_id = exec_resp.json()["execution_id"]
while True:
    status = requests.get(f"{BASE}/execution/{exec_id}/status", headers=headers)
    if status.json()["state"] == "QUERY_STATE_COMPLETED":
        break
    time.sleep(2)
results = requests.get(f"{BASE}/execution/{exec_id}/results", headers=headers)
rows = results.json()["result"]["rows"]
```

### Goldsky Query
```python
import requests
response = requests.post(SUBGRAPH_URL, json={"query": QUERY, "variables": vars})
data = response.json()["data"]
```

### Polygon RPC
```python
from web3 import Web3
w3 = Web3(Web3.HTTPProvider(RPC_URL))
balance = w3.eth.get_balance(wallet)
usdc = w3.eth.contract(address=USDC, abi=ABI)
balance = usdc.functions.balanceOf(wallet).call()
```

---

## ERROR CODES

### Polymarket
| Code | Meaning |
|------|---------|
| 400 | Bad request |
| 404 | Not found |
| 429 | Rate limited |

### Dune
| Code | Meaning |
|------|---------|
| 400 | Invalid query |
| 401 | Invalid API key |
| 429 | Rate limited |

### Goldsky
| Code | Meaning |
|------|---------|
| 400 | Invalid GraphQL |
| 429 | Rate limited |

### Polygon RPC
| Code | Meaning |
|------|---------|
| -32000 | Invalid input |
| -32001 | Gas limit |

---

## ENVIRONMENT VARIABLES

```
# Required
POLYGON_RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY
DUNE_API_KEY=YOUR_DUNE_KEY
GOLDSKY_API_KEY=YOUR_GOLDSKY_KEY

# Optional
POLYMARKET_API_KEY=  # If you get one
```

---

## SOURCE CODE

| API | Source File |
|-----|-------------|
| Polymarket | `src/data/api_clients.py` |
| Dune | `src/data/dune_client.py` |
| Goldsky | `src/data/subgraph_client.py` |
| Polygon RPC | `src/data/onchain_client.py` |

---

## COMPLETE WORKFLOW EXAMPLE

```python
import requests
from web3 import Web3
import time

# 1. Find market
markets = requests.get(
    "https://gamma.polymarket.com/markets",
    params={"question": "Iran nuclear", "limit": 5}
).json()
market = markets[0]
condition_id = market["conditionId"]
clob_token_ids = market["clobTokenIds"]

# 2. Get trades
trades = requests.get(
    "https://data-api.polymarket.com/trades",
    params={"market": condition_id, "limit": 100}
).json()

# 3. Get Dune data
headers = {"x-dune-api-key": DUNE_KEY}
exec_resp = requests.post(
    f"https://api.dune.com/api/v1/query/6964724/execute",
    headers=headers
)
exec_id = exec_resp.json()["execution_id"]
while True:
    status = requests.get(
        f"https://api.dune.com/api/v1/execution/{exec_id}/status",
        headers=headers
    ).json()
    if status["state"] == "QUERY_STATE_COMPLETED":
        break
    time.sleep(2)
dune_trades = requests.get(
    f"https://api.dune.com/api/v1/execution/{exec_id}/results",
    headers=headers
).json()["result"]["rows"]

# 4. Trace on-chain
w3 = Web3(Web3.HTTPProvider(RPC_URL))
usdc = w3.eth.contract(address=USDC, abi=USDC_ABI)
for trader in set(t["user"] for t in trades):
    transfers = usdc.events.Transfer.getLogs(
        fromBlock=0,
        argument_filters={"to": trader}
    )
    # Process transfers
```

---

## SEE ALSO

- [Polymarket API](polymarket.md)
- [Dune API](dune.md)
- [Goldsky API](goldsky.md)
- [Polygon RPC](polygon-rpc.md)
- [Alchemy API](alchemy.md)