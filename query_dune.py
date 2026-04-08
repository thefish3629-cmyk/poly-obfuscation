import requests
import time

DUNE_API_KEY = "XRdFWOXj9uJf7fY7EABjrfFxwhsw26DL"

# First, get the trades from Dune for Israel/Iran nuclear
print("Querying Dune for Iran nuclear market trades...")

# Run a query to get the market's trades
query_id = 2435483  # Polymarket trades query
url = f"https://api.dune.com/api/v1/query/{query_id}/execute"

payload = {
    "query_parameters": [
        {"name": "market_filter", "type": "text", "value": "%iran%"}
    ]
}

headers = {"x-dune-api-key": DUNE_API_KEY}
response = requests.post(url, json=payload, headers=headers)

print(f"Query status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    exec_id = data.get("execution_id")
    print(f"Execution ID: {exec_id}")
    
    # Wait for results
    print("Waiting for results...")
    for i in range(30):
        time.sleep(5)
        status_url = f"https://api.dune.com/api/v1/execution/{exec_id}/status"
        status_resp = requests.get(status_url, headers=headers)
        status_data = status_resp.json()
        state = status_data.get("state")
        print(f"  Attempt {i+1}: {state}")
        if state == "QUERY_STATE_COMPLETED":
            # Get results
            results_url = f"https://api.dune.com/api/v1/execution/{exec_id}/results"
            results_resp = requests.get(results_url, headers=headers)
            results = results_resp.json()
            rows = results.get("result", {}).get("rows", [])
            print(f"\nFound {len(rows)} trades")
            if rows:
                print(f"Sample: {rows[0]}")
            break
        elif state == "QUERY_STATE_FAILED":
            print(f"Query failed: {status_data}")
            break
else:
    print(f"Error: {response.text}")
