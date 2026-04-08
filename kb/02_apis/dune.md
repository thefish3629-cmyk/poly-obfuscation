# Dune Analytics API

API for executing SQL queries on blockchain data.

## Base URL

```
https://api.dune.com/api/v1
```

## Authentication

Header required:
```
x-dune-api-key: YOUR_API_KEY
```

Get API key at [dune.com](https://dune.com/settings/api).

## Endpoints

### POST /query/{query_id}/execute

Execute a saved query.

**Example:**
```
POST https://api.dune.com/api/v1/query/2435483/execute
```

**Headers:**
```
x-dune-api-key: YOUR_KEY
```

**Response:**
```json
{
  "execution_id": "abc123-def456",
  "state": "QUERY_STATE_EXECUTING"
}
```

---

### GET /execution/{execution_id}/status

Check execution status.

**Example:**
```
GET https://api.dune.com/api/v1/execution/abc123-def456/status
```

**Response:**
```json
{
  "execution_id": "abc123-def456",
  "state": "QUERY_STATE_COMPLETED",
  "generated_at": "2024-01-01T12:00:00Z"
}
```

Possible states:
- `QUERY_STATE_EXECUTING` - Running
- `QUERY_STATE_FAILED` - Error
- `QUERY_STATE_COMPLETED` - Done

---

### GET /execution/{execution_id}/results

Get results when complete.

**Example:**
```
GET https://api.dune.com/api/v1/execution/abc123-def456/results
```

**Response:**
```json
{
  "execution_id": "abc123-def456",
  "result": {
    "rows": [
      {"column1": "value1", "column2": 123},
      {"column1": "value2", "column2": 456}
    ],
    "columns": ["column1", "column2"]
  }
}
```

---

### POST /query/insert

Run raw SQL (pro only).

## Execution Flow

```
1. Execute query → get execution_id
2. Poll status until COMPLETED
3. Fetch results
```

### Python Example

```python
import requests
import time

DUNE_KEY = "YOUR_API_KEY"
QUERY_ID = 2435483
BASE = "https://api.dune.com/api/v1"

headers = {"x-dune-api-key": DUNE_KEY}

# 1. Execute
resp = requests.post(f"{BASE}/query/{QUERY_ID}/execute", headers=headers)
exec_id = resp.json()["execution_id"]

# 2. Poll status
while True:
    status = requests.get(f"{BASE}/execution/{exec_id}/status", headers=headers)
    state = status.json()["state"]
    if state == "QUERY_STATE_COMPLETED":
        break
    time.sleep(2)

# 3. Get results
results = requests.get(f"{BASE}/execution/{exec_id}/results", headers=headers)
data = results.json()["result"]["rows"]
```

## Pre-built Queries

Find query IDs at [dune.com/queries](https://dune.com/queries).

### Useful Queries

| Query Name | ID | Description |
|------------|---|-------------|
| Polymarket Trades | 2435483 | Recent trades on Polymarket |

## Rate Limits

| Plan | Limit |
|------|-------|
| Free | 10 queries/day |
| Pro | 100 queries/day |
| Enterprise | Unlimited |

## Errors

| Code | Meaning |
|------|---------|
| 400 | Invalid query |
| 401 | Invalid API key |
| 429 | Rate limited |

## See Also

- [Quick Reference](_endpoints.md)
- [Polymarket API](polymarket.md)
- [Source Code](../../src/data/dune_client.py)