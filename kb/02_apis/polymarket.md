# Polymarket API

Complete API reference for Polymarket markets, trades, and positions.

## Base URLs

| Service | URL | Use Case |
|---------|-----|---------|
| Gamma | `https://gamma.polymarket.com` | Primary market search/querying |
| CLOB | `https://clob.polymarket.com` | Order book, prices, CLOB-specific |
| Data | `https://data-api.polymarket.com` | Trades, positions, activity |
| API | `https://api.polymarket.com` | Fallback when gamma rate limited |

## Authentication

No authentication required for public data endpoints.

**Required headers for all requests:**
```http
Accept: application/json
Content-Type: application/json
```

---

## ENDPOINTS

### GET /markets

Search markets by question text, slug, or other filters.

**URL:** `GET https://gamma.polymarket.com/markets`

**Parameters:**
| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| question | string | No | Search by question text (partial match) | `iran nuke` |
| slug | string | No | Search by URL slug | `iran-strike-...` |
| limit | int | No | Results limit (default 10) | `100` |
| closed | bool | No | Filter by closed status | `true` or `false` |
| condition_id | string | No | Exact condition ID | `0x123...` |

**curl:**
```bash
curl "https://gamma.polymarket.com/markets?question=iran&limit=5"
```

**Python:**
```python
import requests

response = requests.get(
    "https://gamma.polymarket.com/markets",
    params={
        "question": "iran",
        "limit": 5
    }
)
markets = response.json()
```

**Full Response Example:**
```json
[
  {
    "conditionId": "0x1234567890abcdef1234567890abcdef",
    "question": "Will Israel strike Iranian nuclear facility before July?",
    "slug": "israel-strike-iran-nuclear-facility-before-july",
    "description": "This market will resolve to Yes if...",
    "extraInfo": "https://news.com/article",
    "image": "https://polymarket.com/image.jpg",
    "clobTokenIds": ["t-12345-yes", "t-12345-no"],
    "icon": "🇮🇱",
    "groupItemTitle": "Israel strikes Iran",
    "volume": 1500000,
    "liquidity": 500000,
    "spread": 0.02,
    "outcomePrices": {"t-12345-yes": "0.65", "t-12345-no": "0.35"},
    "closed": false,
    "endDate": null,
    "gameStartTime": null,
    "acceptingOrders": true,
    "acceptingLIQUIDITY": true,
    "inactive": false,
    "lastTrade": 1700000000,
    "lastActive": 1700000000,
    "createdAt": 1700000000
  }
]
```

**Error Handling:**
| Status | Cause | Solution |
|--------|-------|----------|
| 400 | Invalid parameter | Check params are URL encoded |
| 429 | Rate limited | Switch to `api.polymarket.com` or add delay |
| 500 | Server error | Retry with exponential backoff |

---

### GET /markets/{conditionId}

Get detailed market info by condition ID.

**URL:** `GET https://gamma.polymarket.com/markets/{conditionId}`

**curl:**
```bash
curl "https://gamma.polymarket.com/markets/0x1234567890abcdef"
```

**Python:**
```python
condition_id = "0x1234567890abcdef"
response = requests.get(
    f"https://gamma.polymarket.com/markets/{condition_id}"
)
market = response.json()
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| conditionId | string | Unique market ID |
| question | string | Market question |
| description | string | Full description |
| extraInfo | string | Resolution source URL |
| clobTokenIds | string[] | [YES_token, NO_token] |
| volume | int | Total volume in cents |
| openInterest | int | Open interest |
| closed | bool | Market resolved? |

**Error Handling:**
| Status | Cause | Solution |
|--------|-------|----------|
| 404 | Market not found | Check conditionId is correct |
| 400 | Invalid conditionId format | Must be hex string with 0x prefix |

---

### GET /markets?slug={slug}

Get market by URL slug.

**URL:** `GET https://gamma.polymarket.com/markets?slug={slug}`

**Python:**
```python
slug = "israel-strike-iran-nuclear-facility-before-july"
response = requests.get(
    "https://gamma.polymarket.com/markets",
    params={"slug": slug}
)
market = response.json()[0]
```

---

### GET /clob-markets

Get CLOB-specific market data (alternative endpoint).

**URL:** `GET https://clob.polymarket.com/markets`

**Python:**
```python
response = requests.get(
    "https://clob.polymarket.com/markets",
    params={"question": "Israel strike Iran"}
)
markets = response.json()
```

**Use Case:** Fallback when gamma returns incomplete data.

---

### GET /trades

Get trades for a specific market.

**URL:** `GET https://data-api.polymarket.com/trades`

**Parameters:**
| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| market | string | Yes* | Condition ID | `0x123...` |
| user | string | No* | Wallet address | `0xabc...` |
| limit | int | No | Results limit | `100` |
| timestamp_gte | int | No | Min timestamp | `1700000000` |
| timestamp_lte | int | No | Max timestamp | `1700100000` |

*Either `market` or `user` required.

**curl:**
```bash
curl "https://data-api.polymarket.com/trades?market=0x123&limit=100"
```

**Python:**
```python
condition_id = "0x1234567890abcdef"
response = requests.get(
    "https://data-api.polymarket.com/trades",
    params={
        "market": condition_id,
        "limit": 100
    }
)
trades = response.json()
```

**Response:**
```json
[
  {
    "id": "trade-123",
    "market": "0x1234567890abcdef",
    "outcome": "Yes",
    "price": 0.65,
    "amount": 100000,
    "side": "BUY",
    "user": "0xabcdef123456789",
    "fee": 250,
    "feeToken": "USDC",
    "timestamp": 1700000000,
    "blockNumber": 50000000,
    "txHash": "0xabc123..."
  }
]
```

**Error Handling:**
| Status | Cause | Solution |
|--------|-------|----------|
| 400 | Invalid market format | Check conditionId is valid hex |
| 429 | Rate limited | Add delay, try again |

---

### GET /trades?user={address}

Get all trades for a specific user/wallet.

**URL:** `GET https://data-api.polymarket.com/trades?user={address}`

**Python:**
```python
user_address = "0x1234567890abcdef1234567890abcdef"
response = requests.get(
    "https://data-api.polymarket.com/trades",
    params={
        "user": user_address,
        "limit": 100
    }
)
user_trades = response.json()
```

---

### GET /positions

Get current positions for a user.

**URL:** `GET https://data-api.polymarket.com/positions`

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| user | string | Yes | Wallet address |

**curl:**
```bash
curl "https://data-api.polymarket.com/positions?user=0x1234567890abcdef"
```

**Python:**
```python
user_address = "0x1234567890abcdef1234567890abcdef"
response = requests.get(
    "https://data-api.polymarket.com/positions",
    params={"user": user_address}
)
positions = response.json()
```

**Response:**
```json
[
  {
    "address": "0x1234567890abcdef1234567890abcdef",
    "conditionId": "0xabc...",
    "outcome": "Yes",
    "balance": 100000,
    "realizePnl": 5000,
    "closed": false
  }
]
```

**Note:** Balance is in units (not cents). Divide by 100 for USDC value.

---

### GET /activity

Get user activity (splits, merges, redemptions).

**URL:** `GET https://data-api.polymarket.com/activity`

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| user | string | Yes | Wallet address |

**Response:**
```json
[
  {
    "id": "split-123",
    "type": "split|merge|redemption",
    "user": "0x123...",
    "collateralAmount": 100000,
    "YESAmount": 50000,
    "NOAmount": 50000,
    "timestamp": 1700000000
  }
]
```

**Python:**
```python
user_address = "0x1234567890abcdef1234567890abcdef"
response = requests.get(
    "https://data-api.polymarket.com/activity",
    params={"user": user_address}
)
activity = response.json()
```

---

### GET /order-book/{tokenId}

Get order book for a CLOB token.

**URL:** `GET https://clob.polymarket.com/order-book/{tokenId}`

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| tokenId | string | CLOB token ID (e.g., `t-12345-yes`) |

**curl:**
```bash
curl "https://clob.polymarket.com/order-book/t-12345-yes"
```

**Python:**
```python
token_id = "t-12345-yes"
response = requests.get(
    f"https://clob.polymarket.com/order-book/{token_id}"
)
order_book = response.json()
```

**Response:**
```json
{
  "bids": [
    [0.64, 50000, "0xabc..."],
    [0.63, 100000, "0xdef..."]
  ],
  "asks": [
    [0.66, 25000, "0x123..."],
    [0.67, 75000, "0x456..."]
  ]
}
```

**Format:** `[price_in_cents, size_in_units, maker_address]`

**Spread Calculation:**
```python
best_bid = float(order_book["bids"][0][0]) / 100
best_ask = float(order_book["asks"][0][0]) / 100
spread = best_ask - best_bid
```

---

### GET /prices-history

Get historical price data for a token.

**URL:** `GET https://clob.polymarket.com/prices-history`

**Parameters:**
| Name | Type | Required | Description | Values |
|------|------|----------|-------------|--------|
| token_id | string | Yes | CLOB token ID | `t-123-yes` |
| interval | string | No | Time interval | `1m`, `15m`, `1h`, `1d`, `1w` |
| before_timestamp | int | No | Before this time | Unix timestamp |
| limit | int | No | Max results | `1000` |

**curl:**
```bash
curl "https://clob.polymarket.com/prices-history?token_id=t-123-yes&interval=1h"
```

**Python:**
```python
response = requests.get(
    "https://clob.polymarket.com/prices-history",
    params={
        "token_id": "t-12345-yes",
        "interval": "1h",
        "limit": 24
    }
)
prices = response.json()
```

**Response:**
```json
[
  {"timestamp": 1700000000, "price": 0.65, "size": 100000},
  {"timestamp": 1700003600, "price": 0.66, "size": 50000}
]
```

---

## COMPLETE ERROR HANDLING

### Error Response Format

```json
{
  "error": "Error message",
  "code": 400
}
```

### Status Codes

| Code | Cause | Solution |
|------|-------|----------|
| 400 | Invalid parameter | Validate params |
| 404 | Resource missing | Check ID/slug |
| 429 | Rate Limited | Backoff + retry |
| 500 | Server error | Exponential backoff |

### 429 Rate Limit Recovery

```python
import time

MAX_RETRIES = 3
DELAY = 2

for attempt in range(MAX_RETRIES):
    response = requests.get(url, params=params)
    if response.status_code == 429:
        wait_time = DELAY * (2 ** attempt)
        time.sleep(wait_time)
        continue
    response.raise_for_status()
    break
```

### Automatic Fallback Chain

```python
def get_markets_with_fallback(query, limit=10):
    endpoints = [
        "https://gamma.polymarket.com/markets",
        "https://clob.polymarket.com/markets",
        "https://api.polymarket.com/markets"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(
                endpoint,
                params={"question": query, "limit": limit}
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            continue
    
    return []
```

---

## RATE LIMITS

| Endpoint | Limit | Notes |
|----------|-------|-------|
| /trades (data-api) | 10 req/sec | Works reliably |
| /positions | 5 req/sec | Works reliably |
| /markets (gamma) | 10 req/sec | May fail in some DNS environments |
| /trades | 10 req/sec | Historical data |
| /positions | 5 req/sec | User data |
| /order-book | 5 req/sec | Real-time data |
| /prices-history | 5 req/sec | Historical |

**Best Practices:**
- Cache frequently accessed data
- Use `limit` parameter
- Use fallback endpoints when rate limited

---

## PYTHON CLIENT WRAPPER

From `src/data/api_clients.py`:

```python
class PolymarketClient:
    GAMMA_BASE = "https://gamma.polymarket.com"
    API_BASE = "https://clob.polymarket.com"
    DATA_BASE = "https://data-api.polymarket.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
    
    def search_markets(self, query: str) -> List[Dict]:
        response = self.session.get(
            f"{self.GAMMA_BASE}/markets",
            params={"question": query, "limit": 10}
        )
        response.raise_for_status()
        return response.json()
    
    def get_market_trades(self, market_id: str, limit: int = 100) -> List[Dict]:
        response = self.session.get(
            f"{self.DATA_BASE}/trades",
            params={"market": market_id, "limit": limit}
        )
        response.raise_for_status()
        return response.json()
    
    def get_user_positions(self, user_address: str) -> List[Dict]:
        response = self.session.get(
            f"{self.DATA_BASE}/positions",
            params={"user": user_address}
        )
        response.raise_for_status()
        return response.json()
    
    def get_order_book(self, token_id: str) -> Dict:
        response = self.session.get(
            f"{self.API_BASE}/order-book/{token_id}"
        )
        response.raise_for_status()
        return response.json()
```

---

## COMMON QUERIES

### Find Specific Market

```python
client = PolymarketClient()
market = client.get_market_by_question("Israel strike on Iranian nuclear facility before July")

# Or by slug
market = client.get_market_by_slug("israel-strike-iran-nuclear-facility-before-july")
```

### Get Market Traders

```python
client = PolymarketClient()
trades = client.get_market_trades(market_id="0x1234567890abcdef", limit=1000)

traders = set(t["user"] for t in trades)
print(f"Unique traders: {len(traders)}")

from collections import Counter
volumes = Counter(t["user"] for t in trades)
top_traders = volumes.most_common(10)
```

### Monitor a Wallet

```python
def monitor_wallet(address):
    client = PolymarketClient()
    
    activity = client.get_user_activity(address)
    positions = client.get_user_positions(address)
    trades = client.session.get(
        f"{client.DATA_BASE}/trades",
        params={"user": address, "limit": 100}
    ).json()
    
    return {"activity": len(activity), "positions": len(positions), "trades": len(trades)}
```

---

## QUICK REFERENCE

| Endpoint | URL | Main Params |
|----------|-----|------------|
| Search markets | `/markets` | `question`, `slug`, `limit` |
| Market details | `/markets/{id}` | conditionId |
| Get trades | `/trades` | `market` OR `user`, `limit` |
| Get positions | `/positions` | `user` |
| Get activity | `/activity` | `user` |
| Order book | `/order-book/{token}` | tokenId |
| Price history | `/prices-history` | `token_id`, `interval` |

---

## SEE ALSO

- [Platform Documentation](../03_polymarket/how-it-works.md)
- [Quick Reference](_endpoints.md)
- [CLOB Token IDs](../03_polymarket/clob-token-ids.md)
- Source: `src/data/api_clients.py`