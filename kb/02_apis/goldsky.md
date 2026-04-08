# Goldsky Subgraph API

API for querying The Graph subgraphs via Goldsky.

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

## Subgraphs Available

### Polymarket
```
https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs
```

Query endpoint: `/graphql`

## GraphQL Queries

### Basic Query

```graphql
{
  markets(first: 5) {
    id
    question
    volume
    clobTokenIds
  }
}
```

### With Filter

```graphql
{
  markets(where: {closed: false}, first: 10) {
    id
    question
    volume
  }
}
```

## Python Example

```python
import requests

SUBGRAPH_URL = (
    "https://api.goldsky.com/api/public/"
    "project_cl6mb8i9h0003e201j6li0diw/subgraphs/graphql"
)

query = """
{
  markets(first: 5) {
    id
    question
    volume
  }
}
"""

response = requests.post(
    SUBGRAPH_URL,
    json={"query": query}
)
data = response.json()
```

## Entities

### Market
| Field | Type | Description |
|-------|------|-------------|
| id | string | Condition ID |
| question | string | Market question |
| volume | int | Trading volume |
| closed | bool | Market closed |
| clobTokenIds | string[] | CLOB token IDs |

### Trade
| Field | Type | Description |
|-------|------|-------------|
| id | string | Trade ID |
| market | string | Market ID |
| account | string | Trader address |
| size | int | Trade size |
| price | int | Trade price |
| timestamp | int | Unix timestamp |

## Filtering

```graphql
{
  trades(
    where: {market: "0x123..."},
    orderBy: timestamp,
    orderDirection: desc,
    first: 100
  ) {
    id
    account
    size
    price
  }
}
```

## Rate Limits

| Plan | Limit |
|------|-------|
| Free | 10K queries/day |
| Pro | 100K queries/day |

## Errors

| Code | Meaning |
|------|---------|
| 400 | Invalid query |
| 401 | Invalid API key |
| 429 | Rate limited |

## See Also

- [Quick Reference](_endpoints.md)
- [Polymarket API](polymarket.md)
- [Source Code](../../src/data/subgraph_client.py)