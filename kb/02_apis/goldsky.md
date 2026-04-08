# Goldsky Subgraph API

Complete API reference for querying Polymarket subgraphs via Goldsky.

## Base URL

```
https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs
```

## Authentication

Header (optional for public subgraphs):
```
x-api-key: YOUR_API_KEY
```

Get API key at [goldsky.com](https://goldsky.com).

---

## SUBGRAPHS AVAILABLE

### Orderbook Subgraph

**Path:** `/orderbook-subgraph/0.0.1/gn`

**What it gets:** Order fills, trades, market data

**URL:** `https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/orderbook-subgraph/0.0.1/gn`

### Positions Subgraph

**Path:** `/positions-subgraph/0.0.7/gn`

**What it gets:** User token balances, positions

**URL:** `https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/positions-subgraph/0.0.7/gn`

### Activity Subgraph

**Path:** `/activity-subgraph/0.0.4/gn`

**What it gets:** Splits, merges, redemptions

**URL:** `https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/activity-subgraph/0.0.4/gn`

### PnL Subgraph

**Path:** `/pnl-subgraph/0.0.14/gn`

**What it gets:** Market conditions, PnL data

**URL:** `https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/pnl-subgraph/0.0.14/gn`

---

## GRAPHQL QUERIES

### Orderbook Subgraph Queries

#### Get Trades for a Market

```graphql
query GetTrades($conditionId: String!, $first: Int!, $skip: Int!) {
  orderFilleds(
    where: {conditionId: $conditionId}
    first: $first
    skip: $skip
    orderBy: timestamp
    orderDirection: desc
  ) {
    id
    transactionHash
    blockNumber
    timestamp
    maker
    taker
    makerAmountFilled
    takerAmountFilled
    makerFee
    takerFee
    conditionId
    makerAssetId
    takerAssetId
    isLiquidation
  }
}
```

**Python:**
```python
import requests

SUBGRAPH_URL = (
    "https://api.goldsky.com/api/public/"
    "project_cl6mb8i9h0003e201j6li0diw/subgraphs/"
    "orderbook-subgraph/0.0.1/gn"
)

query = """
query GetTrades($conditionId: String!, $first: Int!, $skip: Int!) {
  orderFilleds(
    where: {conditionId: $conditionId}
    first: $first
    skip: $skip
    orderBy: timestamp
    orderDirection: desc
  ) {
    id
    transactionHash
    blockNumber
    timestamp
    maker
    taker
    makerAmountFilled
    takerAmountFilled
    conditionId
  }
}
"""

variables = {
    "conditionId": "0x1234567890abcdef",
    "first": 100,
    "skip": 0
}

response = requests.post(
    SUBGRAPH_URL,
    json={"query": query, "variables": variables}
)
data = response.json()
trades = data.get("data", {}).get("orderFilleds", [])
```

**Response:**
```json
{
  "data": {
    "orderFilleds": [
      {
        "id": "0-0",
        "transactionHash": "0xabc123...",
        "blockNumber": "50000000",
        "timestamp": "1700000000",
        "maker": "0xmaker...",
        "taker": "0xtaker...",
        "makerAmountFilled": "100000000",
        "takerAmountFilled": "65000000",
        "makerFee": "250000",
        "takerFee": "162500",
        "conditionId": "0x123...",
        "makerAssetId": "t-123-yes",
        "takerAssetId": "t-123-no",
        "isLiquidation": false
      }
    ]
  }
}
```

**Field Mapping:**
| Field | Type | Description |
|-------|------|-------------|
| makerAmountFilled | string | Maker fill amount (units) |
| takerAmountFilled | string | Taker fill amount (units) |
| makerFee | string | Maker fee (units) |
| takerFee | string | Taker fee (units) |
| isLiquidation | boolean | Liquidation trade? |

**Note:** All amount fields are in units (not cents). Divide by 1e6 for USDC value.

---

#### Get All Order Fills (No Filter)

```graphql
{
  orderFilleds(first: 100, orderBy: timestamp, orderDirection: desc) {
    id
    transactionHash
    blockNumber
    timestamp
    maker
    taker
    makerAmountFilled
    takerAmountFilled
    conditionId
  }
}
```

---

### Positions Subgraph Queries

#### Get User Balances

```graphql
query GetBalances($user: String!) {
  userBalances(where: {user: $user}) {
    id
    user
    balance
    netBalance
    condition {
      id
      questionId
    }
  }
}
```

**Python:**
```python
query = """
query GetBalances($user: String!) {
  userBalances(where: {user: $user}) {
    id
    user
    balance
    netBalance
    condition {
      id
      questionId
    }
  }
}
"""

variables = {"user": "0x1234567890abcdef1234567890abcdef"}

response = requests.post(
    "https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/positions-subgraph/0.0.7/gn",
    json={"query": query, "variables": variables}
)
data = response.json()
balances = data.get("data", {}).get("userBalances", [])
```

**Response:**
```json
{
  "data": {
    "userBalances": [
      {
        "id": "0x123...-0xcondition...",
        "user": "0x123...",
        "balance": "100000000",
        "netBalance": "50000000",
        "condition": {
          "id": "0xcondition...",
          "questionId": "12345"
        }
      }
    ]
  }
}
```

**Field Mapping:**
| Field | Type | Description |
|-------|------|-------------|
| balance | string | Current balance (units) |
| netBalance | string | Net P&L (units) |
| condition.id | string | Market condition ID |
| condition.questionId | string | Market question ID |

---

#### Get All User Balances

```graphql
{
  userBalances(first: 100) {
    id
    user
    balance
    netBalance
    condition {
      id
      questionId
    }
  }
}
```

---

### Activity Subgraph Queries

#### Get User Activity (Splits, Merges, Redemptions)

```graphql
query GetActivity($user: String!, $first: Int!) {
  splits(
    where: {user: $user}
    first: $first
    orderBy: timestamp
    orderDirection: desc
  ) {
    id
    user
    collateralAmount
    timestamp
    transactionHash
  }
  merges(
    where: {user: $user}
    first: $first
    orderBy: timestamp
    orderDirection: desc
  ) {
    id
    user
    collateralAmount
    timestamp
    transactionHash
  }
  redemptions(
    where: {user: $user}
    first: $first
    orderBy: timestamp
    orderDirection: desc
  ) {
    id
    redeemer
    collateralAmount
    timestamp
    transactionHash
  }
}
```

**Python:**
```python
query = """
query GetActivity($user: String!, $first: Int!) {
  splits(where: {user: $user}, first: $first, orderBy: timestamp, orderDirection: desc) {
    id
    user
    collateralAmount
    timestamp
    transactionHash
  }
  merges(where: {user: $user}, first: $first, orderBy: timestamp, orderDirection: desc) {
    id
    user
    collateralAmount
    timestamp
    transactionHash
  }
  redemptions(where: {user: $user}, first: $first, orderBy: timestamp, orderDirection: desc) {
    id
    redeemer
    collateralAmount
    timestamp
    transactionHash
  }
}
"""

variables = {
    "user": "0x1234567890abcdef1234567890abcdef",
    "first": 100
}

response = requests.post(
    "https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/activity-subgraph/0.0.4/gn",
    json={"query": query, "variables": variables}
)
data = response.json()
```

**Response:**
```json
{
  "data": {
    "splits": [
      {
        "id": "split-123",
        "user": "0x123...",
        "collateralAmount": "100000000",
        "timestamp": "1700000000",
        "transactionHash": "0xabc..."
      }
    ],
    "merges": [...],
    "redemptions": [...]
  }
}
```

**Field Mapping:**
| Field | Type | Description |
|-------|------|-------------|
| collateralAmount | string | Amount in USDC units |
| timestamp | string | Unix timestamp |
| transactionHash | string | Transaction hash |

---

### PnL Subgraph Queries

#### Get Market Conditions

```graphql
query GetConditions($conditionId: String!) {
  marketConditions(where: {conditionId: $conditionId}) {
    id
    conditionId
    questionId
    openInterest
    question {
      title
    }
  }
}
```

**Python:**
```python
query = """
query GetConditions($conditionId: String!) {
  marketConditions(where: {conditionId: $conditionId}) {
    id
    conditionId
    questionId
    openInterest
    question {
      title
    }
  }
}
"""

variables = {"conditionId": "0x1234567890abcdef"}

response = requests.post(
    "https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/pnl-subgraph/0.0.14/gn",
    json={"query": query, "variables": variables}
)
data = response.json()
```

---

## PYTHON CLIENT WRAPPER

From `src/data/subgraph_client.py`:

```python
class GoldskyClient:
    BASE_URL = "https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs"
    
    SUBGRAPHS = {
        "orderbook": "/orderbook-subgraph/0.0.1/gn",
        "positions": "/positions-subgraph/0.0.7/gn",
        "activity": "/activity-subgraph/0.0.4/gn",
        "pnl": "/pnl-subgraph/0.0.14/gn",
    }
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"x-api-key": api_key})
    
    def _query(self, subgraph: str, query: str, variables: Dict = None) -> Dict:
        url = f"{self.BASE_URL}{self.SUBGRAPHS[subgraph]}"
        response = self.session.post(
            url,
            json={"query": query, "variables": variables} if variables else {"query": query}
        )
        response.raise_for_status()
        data = response.json()
        if "errors" in data:
            logger.error(f"GraphQL errors: {data['errors']}")
        return data.get("data", {})
    
    def get_trades_for_market(self, condition_id: str, first: int = 1000, skip: int = 0):
        query = """
        query GetTrades($conditionId: String!, $first: Int!, $skip: Int!) {
          orderFilleds(
            where: {conditionId: $conditionId}
            first: $first
            skip: $skip
            orderBy: timestamp
            orderDirection: desc
          ) {
            id
            transactionHash
            blockNumber
            timestamp
            maker
            taker
            makerAmountFilled
            takerAmountFilled
            conditionId
          }
        }
        """
        data = self._query("orderbook", query, {
            "conditionId": condition_id,
            "first": first,
            "skip": skip
        })
        return data.get("orderFilleds", [])
    
    def get_user_balances(self, user_address: str):
        query = """
        query GetBalances($user: String!) {
          userBalances(where: {user: $user}) {
            id
            user
            balance
            netBalance
            condition {
              id
              questionId
            }
          }
        }
        """
        data = self._query("positions", query, {"user": user_address.lower()})
        return data.get("userBalances", [])
    
    def get_user_activity(self, user_address: str, first: int = 100):
        query = """
        query GetActivity($user: String!, $first: Int!) {
          splits(where: {user: $user}, first: $first, orderBy: timestamp, orderDirection: desc) {
            id
            user
            collateralAmount
            timestamp
          }
          merges(where: {user: $user}, first: $first, orderBy: timestamp, orderDirection: desc) {
            id
            user
            collateralAmount
            timestamp
          }
          redemptions(where: {user: $user}, first: $first, orderBy: timestamp, orderDirection: desc) {
            id
            redeemer
            collateralAmount
            timestamp
          }
        }
        """
        data = self._query("activity", query, {"user": user_address.lower(), "first": first})
        return data
```

---

## COMPLETE ERROR HANDLING

### Error Response Format

```json
{
  "errors": [
    {
      "message": "Error message",
      "locations": [{"line": 1, "column": 2}],
      "path": ["query"]
    }
  ]
}
```

### Status Codes

| Code | Cause | Solution |
|------|-------|----------|
| 400 | Invalid query | Check GraphQL syntax |
| 401 | Invalid API key | Verify API key |
| 429 | Rate limited | Add delay + retry |
| 500 | Server error | Retry |

### Retry Logic

```python
import time

MAX_RETRIES = 3
DELAY = 2

for attempt in range(MAX_RETRIES):
    response = requests.post(url, json={"query": query})
    if response.status_code == 429:
        wait_time = DELAY * (2 ** attempt)
        time.sleep(wait_time)
        continue
    response.raise_for_status()
    break
```

---

## PAGINATION

Use `first` and `skip` for pagination:

```python
def get_all_trades(condition_id, batch_size=1000):
    all_trades = []
    skip = 0
    
    while True:
        data = client._query("orderbook", TRADES_QUERY, {
            "conditionId": condition_id,
            "first": batch_size,
            "skip": skip
        })
        batch = data.get("orderFilleds", [])
        
        if not batch:
            break
        
        all_trades.extend(batch)
        
        if len(batch) < batch_size:
            break
        
        skip += batch_size
    
    return all_trades
```

---

## RATE LIMITS

| Plan | Daily Queries | Notes |
|------|-------------|-------|
| Free | 10K | Public subgraphs |
| Pro | 100K | Private + custom |
| Enterprise | Unlimited | + Webhooks |

**Best Practices:**
- Cache frequently accessed data
- Use pagination to limit response size
- Batch queries when possible

---

## COMMON QUERIES

### Get All Trades Paginated

```python
def get_all_trades_for_market(condition_id, max_trades=10000):
    """Get all trades for a market with pagination."""
    trades = []
    skip = 0
    batch_size = 1000
    
    while len(trades) < max_trades:
        data = goldsky._query("orderbook", """
            query GetTrades($conditionId: String!, $first: Int!, $skip: Int!) {
              orderFilleds(
                where: {conditionId: $conditionId}
                first: $first
                skip: $skip
                orderBy: timestamp
                orderDirection: desc
              ) {
                id
                maker
                taker
                makerAmountFilled
                takerAmountFilled
              }
            }
        """, {"conditionId": condition_id, "first": batch_size, "skip": skip})
        
        batch = data.get("orderFilleds", [])
        if not batch:
            break
        
        trades.extend(batch)
        skip += batch_size
        
        if len(batch) < batch_size:
            break
    
    return trades
```

### Get User Portfolio

```python
def get_user_portfolio(user_address):
    """Get full portfolio for a user."""
    balances = goldsky.get_user_balances(user_address)
    activity = goldsky.get_user_activity(user_address)
    
    return {
        "balances": balances,
        "splits": activity.get("splits", []),
        "merges": activity.get("merges", []),
        "redemptions": activity.get("redemptions", [])
    }
```

---

## QUICK REFERENCE

| Subgraph | Path | Main Query |
|---------|------|-----------|
| Orderbook | `/orderbook-subgraph/0.0.1/gn` | orderFilleds |
| Positions | `/positions-subgraph/0.0.7/gn` | userBalances |
| Activity | `/activity-subgraph/0.0.4/gn` | splits, merges, redemptions |
| PnL | `/pnl-subgraph/0.0.14/gn` | marketConditions |

---

## SEE ALSO

- [Quick Reference](_endpoints.md)
- [Polymarket API](polymarket.md)
- Source: `src/data/subgraph_client.py`