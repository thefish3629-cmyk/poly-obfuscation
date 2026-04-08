# Alchemy API

Alchemy provides enhanced access to Polygon blockchain data with higher rate limits and additional methods.

## What is Alchemy

Alchemy is a blockchain infrastructure platform that provides:
- **Enhanced RPC nodes** - More reliable than public RPCs
- **Higher rate limits** - More requests per second
- **Additional APIs** - Methods not in standard RPC
- **WebSocket support** - Real-time subscriptions

## Base URL

```
https://polygon-mainnet.g.alchemy.com/v2/YOUR_API_KEY
```

## How We Use It

We use Alchemy as our **Polygon RPC provider** for:
- Querying wallet balances
- Getting transaction data
- Filtering ERC-20 events
- Tracing fund origins
- Checking contract code

## Authentication

API key in URL path:
```python
RPC_URL = "https://polygon-mainnet.g.alchemy.com/v2/YOUR_API_KEY"

from web3 import Web3
w3 = Web3(Web3.HTTPProvider(RPC_URL))
```

---

## WHAT YOU CAN GET FROM ALCHEMY

### 1. Standard RPC Methods

All standard Polygon RPC methods:

| Method | Description | Example |
|--------|-------------|---------|
| eth_blockNumber | Latest block | `w3.eth.block_number` |
| eth_getBalance | Wallet balance | `w3.eth.get_balance(addr)` |
| eth_getTransactionCount | Nonce | `w3.eth.get_transaction_count(addr)` |
| eth_call | Read contract | `w3.eth.call(tx)` |
| eth_getTransactionReceipt | Receipt | `w3.eth.get_transaction_receipt(hash)` |
| eth_getLogs | Event logs | `w3.eth.get_logs(filter)` |

---

### 2. Enhanced Methods

Alchemy provides additional methods not in standard RPC:

#### debug_traceTransaction

Get detailed execution trace of a transaction.

```python
# Using Alchemy enhanced API
result = w3.provider.make_request(
    "debug_traceTransaction",
    [tx_hash, {"tracer": "callTracer"}]
)

# Parsed call structure
for call in result.get("calls", []):
    print(f"Type: {call['type']}")
    print(f"From: {call['from']}")
    print(f"To: {call['to']}")
    print(f"Value: {call.get('value')}")
    print(f"Input: {call.get('input', '')[:50]}...")
```

**Use Case:** Trace how a transaction moved funds through contracts.

**Response:**
```json
{
  "calls": [
    {
      "type": "CALL",
      "from": "0xabc...",
      "to": "0xdef...",
      "value": "0x0",
      "input": "0xa9059cbb...",
      "output": "0x000000000000000000000000000000000000000000000000000000000000002a"
    }
  ]
}
```

---

#### trace_call

Simulate a transaction without sending it.

```python
# Simulate a contract call
result = w3.provider.make_request(
    "trace_call",
    [
        {
            "from": wallet_address,
            "to": contract_address,
            "data": encoded_function_data
        },
        {"tracer": "callTracer"}
    ]
)
```

**Use Case:** Test how a transaction will behave before sending.

---

#### trace_replayTransaction

Replay a transaction with different states.

```python
result = w3.provider.make_request(
    "trace_replayTransaction",
    [
        tx_hash,
        ["state", "trace"]  # How to replay
    ]
)
```

**Use Case:** Analyze historical transaction execution.

---

### 3. Token APIs (Alchemy SDK)

Alchemy provides token-specific endpoints:

#### Get Token Prices

```python
# Using Alchemy SDK
from alchemy import Alchemy

alchemy = Alchemy(api_key=YOUR_KEY)

# Get token prices
prices = alchemy.getTokenPrices(["USDC", "USDT", "MATIC"])
```

#### Get Token Holders

```python
# Get all holders of a token
holders = alchemy.getTokenHolders(token_address)

for holder in holders["holders"]:
    print(f"Holder: {holder['owner']}")
    print(f"Balance: {holder['balance']}")
```

---

### 4. WebSocket Subscriptions

Real-time event streams.

#### New Block Headers

```python
# Subscribe to new blocks
ws = WebSocketProvider("wss://polygon-mainnet.g.alchemy.com/ws/v2/YOUR_KEY")

# Send subscription
ws.send('{"jsonrpc":"2.0","method":"eth_subscribe","params":["newBlockHeaders"],"id":1}')

# Receive blocks
while True:
    message = ws.recv()
    print(message)
```

#### Pending Transactions

```python
# Subscribe to pending transactions
ws.send('{"jsonrpc":"2.0","method":"eth_subscribe","params":["newPendingTransaction"],"id":1}')
```

#### Event Logs

```python
# Subscribe to specific events
subscription = {
    "jsonrpc": "2.0",
    "method": "eth_subscribe",
    "params": [
        "logs",
        {
            "address": USDC_ADDRESS,
            "topics": ["0xddf252ad..."]  # Transfer event selector
        }
    ],
    "id": 1
}
```

---

### 5. NFT APIs

Get NFT data for collections on Polygon.

#### Get NFT Metadata

```python
# Get NFT metadata
nft = alchemy.nft.getNftMetadata(
    contract_address=collection,
    token_id=token_id
)

print(nft["name"])
print(nft["description"])
print(nft["imageUrl"])
```

#### Get Owner of NFT

```python
owner = alchemy.nft.getNftOwners(
    contract_address=collection,
    token_id=token_id
)
```

---

## ERROR HANDLING

### Connection Errors

```python
if not w3.is_connected():
    raise ConnectionError("Failed to connect to Alchemy")

# Check connection
try:
    block = w3.eth.block_number
except Exception as e:
    print(f"Alchemy error: {e}")
    # Fallback to public RPC
    w3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))
```

### Rate Limit Errors

```python
# Handle 429 errors
if response.status_code == 429:
    wait_time = int(response.headers.get("Retry-After", 60))
    time.sleep(wait_time)
```

---

## RATE LIMITS

| Plan | RPC Calls | Enhanced APIs | WebSockets |
|------|----------|---------------|------------|
| Free | 5/sec | 50/day | 1 connection |
| Growth | 20/sec | 1000/day | 5 connections |
| Scale | 330/sec | 10000/day | 50 connections |

**Best Practices:**
- Cache frequently accessed data
- Use web3.py caching middleware
- Batch requests when possible
- Use webhooks for notifications instead of polling

---

## WEB3.PY CONFIGURATION

### With Automatic Caching

```python
from web3 import Web3
from web3.middleware import cache

w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Add caching middleware
w3.middleware_onion.add(cache)
```

### With Retry Middleware

```python
from web3.middleware.retry import RetryMiddleware

w3.middleware_onion.add(
    RetryMiddleware,
    max_retries=3,
    timeout=30
)
```

---

## ALCHEMY VS PUBLIC RPC

| Feature | Alchemy | Public RPC |
|---------|---------|-----------|
| Reliability | 99.9% uptime | Can go down |
| Rate limits | Higher | Low/Rate limited |
| Enhanced APIs | Yes | No |
| WebSockets | Yes | Limited |
| Debug traces | Yes | No |
| Support | Email | None |

---

## PYTHON EXAMPLE: COMPLETE WORKFLOW

```python
from web3 import Web3

# Connect to Alchemy
RPC_URL = "https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Check connection
print(f"Connected: {w3.is_connected()}")
print(f"Latest block: {w3.eth.block_number}")

# Get wallet balance
wallet = "0x1234567890abcdef1234567890abcdef"
balance = w3.eth.get_balance(wallet)
print(f"MATIC: {w3.from_wei(balance, 'matic')}")

# Get USDC balance
USDC = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa841174"
usdc_abi = [{"name":"balanceOf","type":"function","inputs":[{"name":"owner","type":"address"}],"outputs":[{"name":"","type":"uint256"}]}]

usdc = w3.eth.contract(address=USDC, abi=usdc_abi)
usdc_balance = usdc.functions.balanceOf(wallet).call()
print(f"USDC: {usdc_balance / 1e6}")

# Get recent transactions
from_block = w3.eth.block_number - 1000
events = usdc.events.Transfer.getLogs(
    fromBlock=from_block,
    argument_filters={"to": wallet}
)

print(f"Recent incoming: {len(events)}")
```

---

## ALTERNATIVE RPC PROVIDERS

If Alchemy has issues, alternatives:

| Provider | URL | Notes |
|----------|-----|------|
| Infura | `https://polygon-mainnet.infura.io/v3/KEY` | Good alternative |
| Public | `https://polygon-rpc.com` | Rate limited |
| Ankr | `https://rpc.ankr.com/polygon` | Free tier |

### Fallback Example

```python
RPC_URLS = [
    "https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY",
    "https://polygon-mainnet.infura.io/v3/YOUR_KEY",
    "https://polygon-rpc.com"
]

w3 = None
for url in RPC_URLS:
    w3 = Web3(Web3.HTTPProvider(url))
    if w3.is_connected():
        print(f"Connected via {url}")
        break

if not w3 or not w3.is_connected():
    raise ConnectionError("No RPC available")
```

---

## QUICK REFERENCE

| Need | Method | Alchemy Feature |
|------|--------|---------------|
| Basic queries | Standard RPC | eth_blockNumber, etc. |
| Debug traces | debug_traceTransaction | Enhanced API |
| Simulate tx | trace_call | Enhanced API |
| Real-time | WebSocket | newBlockHeaders |
| Token prices | Alchemy SDK | getTokenPrices |
| NFTs | Alchemy SDK | getNftMetadata |

---

## SEE ALSO

- [Polygon RPC](polygon-rpc.md)
- [Quick Reference](_endpoints.md)
- [Crypto Basics](../01_crypto/)
- [Sign up at alchemy.com](https://alchemy.com)