# Dune Analytics API

Complete API reference for executing SQL queries on blockchain data.

## Base URL

```
https://api.dune.com/api/v1
```

## Authentication

Header required:
```
x-dune-api-key: YOUR_API_KEY
```

Get API key at [dune.com/settings/api](https://dune.com/settings/api).

---

## ENDPOINTS

### POST /query/{query_id}/execute

Execute a saved Dune query.

**URL:** `POST https://api.dune.com/api/v1/query/{query_id}/execute`

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| query_id | int | Yes | Saved query ID |
| parameters | array | No | Query parameters |

**Headers:**
```
x-dune-api-key: YOUR_KEY
Content-Type: application/json
```

**Request (no parameters):**
```bash
curl -X POST "https://api.dune.com/api/v1/query/2435483/execute" \
  -H "x-dune-api-key: YOUR_KEY"
```

**Request (with parameters):**
```bash
curl -X POST "https://api.dune.com/api/v1/query/2435483/execute" \
  -H "x-dune-api-key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"parameters": [
    {"name": "limit", "type": "number", "value": 10000},
    {"name": "condition_id", "type": "text", "value": "0x123..."}
  ]}'
```

**Python:**
```python
import requests

DUNE_KEY = "YOUR_API_KEY"
QUERY_ID = 2435483
BASE = "https://api.dune.com/api/v1"

headers = {"x-dune-api-key": DUNE_KEY}

# Without parameters
response = requests.post(
    f"{BASE}/query/{QUERY_ID}/execute",
    headers=headers
)
result = response.json()

# With parameters (query 6964724 - Iran trades)
payload = {
    "parameters": [
        {"name": "limit", "type": "number", "value": 10000}
    ]
}
response = requests.post(
    f"{BASE}/query/6964724/execute",
    headers=headers,
    json=payload
)
result = response.json()
```

**Response:**
```json
{
  "execution_id": "abc123-def456-789",
  "state": "QUERY_STATE_EXECUTING"
}
```

**Error Handling:**
| Status | Cause | Solution |
|--------|-------|----------|
| 400 | Invalid query ID | Check query_id is valid |
| 401 | Invalid API key | Verify your API key |
| 404 | Query not found | Check query exists in your account |

---

### GET /execution/{execution_id}/status

Check query execution status.

**URL:** `GET https://api.dune.com/api/v1/execution/{execution_id}/status`

**curl:**
```bash
curl "https://api.dune.com/api/v1/execution/abc123-def456-789/status" \
  -H "x-dune-api-key: YOUR_KEY"
```

**Python:**
```python
headers = {"x-dune-api-key": DUNE_KEY}
execution_id = "abc123-def456-789"

response = requests.get(
    f"{BASE}/execution/{execution_id}/status",
    headers=headers
)
status = response.json()
```

**Response:**
```json
{
  "execution_id": "abc123-def456-789",
  "state": "QUERY_STATE_COMPLETED",
  "generated_at": "2024-01-01T12:00:00Z"
}
```

**State Values:**
| State | Meaning |
|-------|---------|
| QUERY_STATE_EXECUTING | Query running, wait |
| QUERY_STATE_FAILED | Query error, check error message |
| QUERY_STATE_COMPLETED | Results ready |

**Error Handling:**
| Status | Cause | Solution |
|--------|-------|----------|
| 404 | Execution not found | Check execution_id |
| 410 | Execution gone | Execute query again |

---

### GET /execution/{execution_id}/results

Get query results when complete.

**URL:** `GET https://api.dune.com/api/v1/execution/{execution_id}/results`

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| limit | int | No | Max rows (default 10000) |

**curl:**
```bash
curl "https://api.dune.com/api/v1/execution/abc123-def456-789/results?limit=10000" \
  -H "x-dune-api-key: YOUR_KEY"
```

**Python:**
```python
headers = {"x-dune-api-key": DUNE_KEY}

response = requests.get(
    f"{BASE}/execution/{execution_id}/results",
    headers=headers,
    params={"limit": 10000}
)
results = response.json()
data = results.get("result", {}).get("rows", [])
```

**Response:**
```json
{
  "execution_id": "abc123-def456-789",
  "result": {
    "rows": [
      {
        "block_time": "2024-01-01T12:00:00Z",
        "tx_hash": "0xabc...",
        "block_number": 50000000,
        "trader": "0x123...",
        "side": "BUY",
        "amount_usd": 1000.00,
        "condition_id": "0xabc..."
      }
    ],
    "columns": ["block_time", "tx_hash", "block_number", "trader", "side", "amount_usd", "condition_id"]
  }
}
```

---

### GET /query (List Queries)

List your saved queries.

**URL:** `GET https://api.dune.com/api/v1/query`

**curl:**
```bash
curl "https://api.dune.com/api/v1/query" \
  -H "x-dune-api-key: YOUR_KEY"
```

**Python:**
```python
response = requests.get(
    f"{BASE}/query",
    headers={"x-dune-api-key": DUNE_KEY}
)
queries = response.json()
```

**Response:**
```json
{
  "result": [
    {
      "id": 6964724,
      "name": "Iran Polymarket Trades",
      "description": "Get trades for Iran markets",
      "created_at": "2024-01-01",
      "last_run": "2024-01-02"
    }
  ]
}
```

---

### POST /query/insert

Run raw SQL query (Pro/Enterprise only).

**URL:** `POST https://api.dune.com/api/v1/query/insert`

**Request:**
```json
{
  "query": "SELECT * FROM polymarket_polygon.market_trades LIMIT 10"
}
```

---

## COMPLETE EXECUTION FLOW

```
1. Execute query → get execution_id
2. Poll status until COMPLETED
3. Fetch results
```

### Full Python Workflow

```python
import requests
import time

DUNE_KEY = "YOUR_API_KEY"
QUERY_ID = 6964724  # Iran trades query
BASE = "https://api.dune.com/api/v1"

headers = {"x-dune-api-key": DUNE_KEY}

# Step 1: Execute
print("Executing query...")
response = requests.post(
    f"{BASE}/query/{QUERY_ID}/execute",
    headers=headers
)
exec_data = response.json()
execution_id = exec_data["execution_id"]
print(f"Execution ID: {execution_id}")

# Step 2: Poll status
print("Waiting for results...")
timeout = 300  # 5 minutes
start = time.time()

while time.time() - start < timeout:
    status_response = requests.get(
        f"{BASE}/execution/{execution_id}/status",
        headers=headers
    )
    status = status_response.json()
    state = status["state"]
    
    if state == "QUERY_STATE_COMPLETED":
        print("Query completed!")
        break
    elif state == "QUERY_STATE_FAILED":
        error_msg = status.get("error", "Unknown error")
        raise Exception(f"Query failed: {error_msg}")
    
    time.sleep(2)  # Poll every 2 seconds
else:
    raise TimeoutError("Query timed out")

# Step 3: Get results
print("Fetching results...")
results_response = requests.get(
    f"{BASE}/execution/{execution_id}/results",
    headers=headers,
    params={"limit": 10000}
)
results = results_response.json()
rows = results.get("result", {}).get("rows", [])

print(f"Got {len(rows)} rows")
```

---

## ERRor handling

### Error Response Format

```json
{
  "execution_id": "abc...",
  "state": "QUERY_STATE_FAILED",
  "error": "Error message"
}
```

### Status Codes

| Code | Cause | Solution |
|------|-------|----------|
| 400 | Invalid query | Check SQL syntax |
| 401 | Invalid API key | Verify key at dune.com |
| 403 | No permission | Upgrade plan |
| 429 | Rate limited | Wait + retry |
| 500 | Server error | Retry |

### Retry Logic

```python
import time

MAX_RETRIES = 3
DELAY = 5

for attempt in range(MAX_RETRIES):
    try:
        response = execute_query(query_id)
        if response.status_code == 200:
            break
    except Exception as e:
        if attempt < MAX_RETRIES - 1:
            wait_time = DELAY * (2 ** attempt)  # Exponential backoff
            print(f"Error: {e}. Retrying in {wait_time}s...")
            time.sleep(wait_time)
        else:
            raise
```

### Timeout Handling

```python
import time

TIMEOUT = 300  # 5 minutes
POLL_INTERVAL = 2

start = time.time()
while time.time() - start < TIMEOUT:
    status = get_status(execution_id)
    if status["state"] == "QUERY_STATE_COMPLETED":
        return get_results(execution_id)
    elif status["state"] == "QUERY_STATE_FAILED":
        raise Exception(f"Query failed: {status.get('error')}")
    time.sleep(POLL_INTERVAL)

raise TimeoutError(f"Query timed out after {TIMEOUT}s")
```

---

## RATE LIMITS

| Plan | Daily Queries | Concurrent | Cache |
|------|-------------|------------|-------|
| Free | 10 | 1 | 15 min |
| Pro | 100 | 5 | 5 min |
| Enterprise | Unlimited | Unlimited | 1 min |

**Best Practices:**
- Use cache (`/results` endpoint caches responses)
- Implement pagination for large results
- Prefer saved queries over raw SQL
- Set up query schedules for recurring data

---

## IMPORTANT QUERIES

### Query 6964724 - Iran Polymarket Trades

Used in `src/data/dune_client.py`.

**Description:** Gets trades for Iran-related Polymarket markets.

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| limit | number | 10000 | Max rows |

**Usage:**
```python
dune = DuneClient(api_key=YOUR_KEY, query_id=6964724)
trades = dune.run_query_and_wait(6964724, timeout=300)
```

### Query 2435483 - Market Trades

Generic market trades query.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| condition_id | text | Market condition ID |
| limit | number | Max rows |

---

## PYTHON CLIENT WRAPPER

From `src/data/dune_client.py`:

```python
class DuneClient:
    BASE_URL = "https://api.dune.com/api/v1"
    DEFAULT_IRAN_QUERY_ID = 6964724
    
    def __init__(self, api_key: str, query_id: int = None):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"x-dune-api-key": api_key})
    
    def execute_query(self, query_id: int, parameters: Dict = None) -> Dict:
        url = f"{self.BASE_URL}/query/{query_id}/execute"
        payload = {"parameters": parameters} if parameters else {}
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_execution_status(self, execution_id: str) -> Dict:
        url = f"{self.BASE_URL}/execution/{execution_id}/status"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_execution_results(self, execution_id: str, limit: int = 10000) -> Dict:
        url = f"{self.BASE_URL}/execution/{execution_id}/results"
        response = self.session.get(url, params={"limit": limit})
        response.raise_for_status()
        return response.json()
    
    def run_query_and_wait(self, query_id: int, timeout: int = 300) -> List[Dict]:
        exec_data = self.execute_query(query_id)
        execution_id = exec_data["execution_id"]
        
        start = time.time()
        while time.time() - start < timeout:
            status = self.get_execution_status(execution_id)
            state = status["state"]
            
            if state == "QUERY_STATE_COMPLETED":
                results = self.get_execution_results(execution_id)
                return results.get("result", {}).get("rows", [])
            elif state == "QUERY_STATE_FAILED":
                raise Exception(f"Query failed: {status}")
            
            time.sleep(2)
        
        raise TimeoutError("Query timed out")
    
    def get_polymarket_trades(self, days: int = 30, limit: int = 10000):
        """Get Polymarket trades using query 6964724."""
        url = f"{self.BASE_URL}/query/6964724/execute"
        payload = {
            "parameters": [
                {"name": "limit", "type": "number", "value": limit}
            ]
        }
        
        response = self.session.post(url, json=payload)
        if response.status_code == 200:
            exec_id = response.json()["execution_id"]
            
            start = time.time()
            while time.time() - start < 300:
                status = self.get_execution_status(exec_id)
                if status["state"] == "QUERY_STATE_COMPLETED":
                    results = self.get_execution_results(exec_id)
                    return results.get("result", {}).get("rows", [])
                time.sleep(3)
        
        return []
```

---

## COMMON QUERIES

### Get All Trades for a Market

```python
def get_market_trades(condition_id, limit=5000):
    """Get all trades for a specific market."""
    url = f"{BASE}/query/2435483/execute"
    payload = {
        "parameters": [
            {"name": "condition_id", "type": "text", "value": condition_id},
            {"name": "limit", "type": "number", "value": limit}
        ]
    }
    
    response = requests.post(url, json=payload, headers=headers)
    exec_id = response.json()["execution_id"]
    
    # Wait for results
    while True:
        status = requests.get(f"{BASE}/execution/{exec_id}/status", headers=headers)
        if status.json()["state"] == "QUERY_STATE_COMPLETED":
            results = requests.get(f"{BASE}/execution/{exec_id}/results", headers=headers)
            return results.json()["result"]["rows"]
        time.sleep(2)
```

### Get Top Traders by Volume

```python
def get_top_traders(condition_id, limit=10):
    """Get top traders by volume for a market."""
    query = f"""
    SELECT trader, SUM(amount_usd) as volume
    FROM polymarket_polygon.market_trades
    WHERE condition_id = '{condition_id}'
    GROUP BY trader
    ORDER BY volume DESC
    LIMIT {limit}
    """
    # Run via /query/insert (Pro only) or use saved query
    results = run_raw_sql(query)
    return sorted(results, key=lambda x: x.get("volume", 0), reverse=True)
```

---

## QUICK REFERENCE

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/query/{id}/execute` | POST | Execute saved query |
| `/execution/{id}/status` | GET | Check status |
| `/execution/{id}/results` | GET | Get results |
| `/query` | GET | List queries |
| `/query/insert` | POST | Run raw SQL |

---

## SEE ALSO

- [Quick Reference](_endpoints.md)
- [Polymarket API](polymarket.md)
- Source: `src/data/dune_client.py`