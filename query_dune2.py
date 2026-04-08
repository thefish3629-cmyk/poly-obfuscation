import requests
import time

DUNE_API_KEY = "XRdFWOXj9uJf7fY7EABjrfFxwhsw26DL"

# Run a simple query to get recent Polymarket trades
print("Getting recent Polymarket trades from Dune...")

url = f"https://api.dune.com/api/v1/query/2435483/execute"
headers = {"x-dune-api-key": DUNE_API_KEY}

payload = {
    "parameters": [
        {"name": "days", "type": "number", "value": 365},
        {"name": "limit", "type": "number", "value": 1000}
    ]
}

response = requests.post(url, json=payload, headers=headers)
print(f"Query status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    exec_id = data.get("execution_id")
    print(f"Execution ID: {exec_id}")
    
    print("Waiting for results...")
    for i in range(20):
        time.sleep(10)
        status_url = f"https://api.dune.com/api/v1/execution/{exec_id}/status"
        status_resp = requests.get(status_url, headers=headers)
        status_data = status_resp.json()
        state = status_data.get("state")
        print(f"  {state}")
        if state == "QUERY_STATE_COMPLETED":
            results_url = f"https://api.dune.com/api/v1/execution/{exec_id}/results"
            results_resp = requests.get(results_url, headers=headers)
            results = results_resp.json()
            rows = results.get("result", {}).get("rows", [])
            print(f"\nFound {len(rows)} trades")
            if rows:
                print(f"Columns: {list(rows[0].keys())}")
                print(f"Sample: {rows[0]}")
            break
        elif state == "QUERY_STATE_FAILED":
            print(f"Failed: {status_data}")
            break
else:
    print(f"Error: {response.text}")
