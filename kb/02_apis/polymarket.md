# Polymarket API

API for querying markets, trades, and positions on Polymarket.

## Base URLs

| Service | URL |
|--------|-----|
| Gamma | `https://gamma.polymarket.com` |
| CLOB | `https://clob.polymarket.com` |
| Data | `https://data-api.polymarket.com` |
| API | `https://api.polymarket.com` |

## Authentication

No authentication required for most endpoints.

Required headers:
```
Accept: application/json
Content-Type: application/json
```

## Endpoints

### GET /markets

Search markets.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| question | string | Search by question text |
| slug | string | Search by slug |
| limit | int | Results limit (default 10) |
| closed | bool | Filter by closed status |

**Example:**
```
GET https://gamma.polymarket.com/markets?question=iran&limit=5
```

**Response:**
```json
[
  {
    "conditionId": "abc123",
    "question": "Will Israel strike Iran before July?",
    "slug": "israel-strike-iran-nuclear-facility-before-july",
    "clobTokenIds": ["t-123", "t-456"],
    "closed": false,
    "volume": 1500000
  }
]
```

---

### GET /markets/{condition_id}

Get specific market details.

**Example:**
```
GET https://gamma.polymarket.com/markets/abc123
```

---

### GET /trades

Get trades for a market.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| market | string | Market condition_id |
| limit | int | Results limit |

**Example:**
```
GET https://data-api.polymarket.com/trades?market=abc123&limit=100
```

**Response:**
```json
[
  {
    "id": "tx-123",
    "market": "abc123",
    "outcome": "yes",
    "price": 0.65,
    "amount": 1000,
    "user": "0xabc...",
    "timestamp": 1700000000
  }
]
```

---

### GET /positions

Get user positions.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| user | string | Wallet address |

**Example:**
```
GET https://data-api.polymarket.com/positions?user=0x123...
```

---

### GET /activity

Get user activity.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| user | string | Wallet address |

**Example:**
```
GET https://data-api.polymarket.com/activity?user=0x123...
```

---

### GET /order-book/{token_id}

Get order book for a token.

**Example:**
```
GET https://clob.polymarket.com/order-book/t-123
```

---

### GET /prices-history

Get historical prices.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| token_id | string | CLOB token ID |
| interval | string | 1h, 1d, 1w |

**Example:**
```
GET https://clob.polymarket.com/prices-history?token_id=t-123&interval=1h
```

## Alternative Endpoints

### api.polymarket.com

Fallback for gamma when rate limited.

```
GET https://api.polymarket.com/markets?question=iran
```

## Common Queries

### Find Iran-Israel Market

```python
import requests

response = requests.get(
    "https://clob.polymarket.com/markets",
    params={"question": "Israel strike on Iranian nuclear facility before July"}
)
market = response.json()[0]
print(market["conditionId"])
```

### Get Recent Trades

```python
response = requests.get(
    "https://data-api.polymarket.com/trades",
    params={"market": condition_id, "limit": 100}
)
trades = response.json()
```

## Rate Limits

- ~10 requests per second
- Higher limits with API key (contact Polymarket)

## Errors

| Code | Meaning |
|------|---------|
| 400 | Bad Request |
| 404 | Market not found |
| 429 | Rate limited |

## See Also

- [Polymarket Platform Docs](../03_polymarket/how-it-works.md)
- [Quick Reference](_endpoints.md)
- [Source Code](../../src/data/api_clients.py)