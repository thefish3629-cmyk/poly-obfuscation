# Polygon RPC

Advanced methods for querying Polygon blockchain data with web3.py.

## Base URLs

### Alchemy (Recommended)
```
https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY
```

### Public (Rate Limited)
```
https://polygon-rpc.com
```

### Infura
```
https://polygon-mainnet.infura.io/v3/YOUR_API_KEY
```

## Authentication

API key in URL path:
```
?apikey=YOUR_KEY
```

Or via web3.py:
```python
from web3 import Web3

w3 = Web3(Web3.HTTPProvider(
    "https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY"
))
```

---

## COMMON CONTRACT ADDRESSES (POLYGON)

| Contract | Address | Description |
|----------|---------|-------------|
| USDC | 0x2791Bca1f2de4661ED88A30C99A7a9449Aa841174 | USD Coin |
| USDT | 0xc2132D05D013c5EF71C41ED0E4aD4B70F5d9a5b6 | Tether |
| WMATIC | 0x0d500B1d8eFAEF0deC5C1651cD344CAb5E3de002 | Wrapped MATIC |
| QUICK | 0xb5C640A6e0d8c5f72A7eB2f4c2d02eEc75715091 | QuickSwap |
| MATIC | 0x0000... | Native MATIC (no address) |

---

## BASIC METHODS

### eth_blockNumber

Get latest block number.

```python
block = w3.eth.block_number
print(f"Latest block: {block}")
```

### eth_getBalance

Get wallet balance.

```python
balance = w3.eth.get_balance(wallet_address)
# Returns in wei
print(f"Balance: {w3.from_wei(balance, 'matic')} MATIC")
```

### eth_getTransactionCount

Get nonce (transaction count) for address.

```python
nonce = w3.eth.get_transaction_count(wallet_address)
print(f"Nonce: {nonce}")
```

### eth_getCode

Get contract bytecode. Returns "0x" if EOA (externally owned account).

```python
code = w3.eth.get_code(contract_address)
is_contract = len(code) > 2
```

---

## ADVANCED METHODS

### Filter ERC-20 Transfer Events

Get all USDC transfers for a specific wallet.

```python
from web3 import Web3

USDC_ADDRESS = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa841174"

w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Get USDC contract
usdc = w3.eth.contract(
    address=w3.to_checksum_address(USDC_ADDRESS),
    abi=[
        {
            "anonymous": False,
            "inputs": [
                {"indexed": True, "name": "from", "type": "address"},
                {"indexed": True, "name": "to", "type": "address"},
                {"indexed": False, "name": "value", "type": "uint256"}
            ],
            "name": "Transfer",
            "type": "event"
        }
    ]
)

# Create filter for incoming transfers
incoming_filter = usdc.events.Transfer.create_filter(
    from_block=0,
    to_block="latest",
    argument_filters={"to": wallet_address}
)

# Get all events
incoming_transfers = []
for event in incoming_filter.get_all_entries():
    incoming_transfers.append({
        "from": event.args["from"],
        "to": event.args["to"],
        "value": event.args["value"] / 1e6,  # USDC has 6 decimals
        "block": event.blockNumber,
        "tx_hash": event.transactionHash.hex()
    })

# Create filter for outgoing transfers
outgoing_filter = usdc.events.Transfer.create_filter(
    from_block=0,
    to_block="latest",
    argument_filters={"from": wallet_address}
)

outgoing_transfers = []
for event in outgoing_filter.get_all_entries():
    outgoing_transfers.append({
        "from": event.args["from"],
        "to": event.args["to"],
        "value": event.args["value"] / 1e6,
        "block": event.blockNumber,
        "tx_hash": event.transactionHash.hex()
    })
```

**Source:** Used in `src/data/onchain_client.py:107-150`.

---

### Trace Fund Origin (Multi-hop)

Trace USDC funding sources through multiple hops.

```python
def trace_fund_origin(w3, address, max_hops=5):
    """Trace USDC funding sources for an address."""
    USDC = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa841174"
    
    all_hops = []
    visited = set()
    queue = [(address.lower(), 0, None, "wallet")]
    
    usdc_contract = w3.eth.contract(
        address=w3.to_checksum_address(USDC),
        abi=[{"name": "Transfer", "type": "event", "inputs": [...]}]
    )
    
    while queue and len(all_hops) < 100:
        current_addr, hop, prev_addr, contract_type = queue.pop(0)
        
        if current_addr in visited or hop >= max_hops:
            continue
        visited.add(current_addr)
        
        # Get incoming transfers
        try:
            transfer_filter = usdc_contract.events.Transfer.create_filter(
                from_block=0,
                to_block="latest",
                argument_filters={"to": current_addr}
            )
            
            for event in transfer_filter.get_all_entries():
                from_addr = event.args["from"].lower()
                to_addr = event.args["to"].lower()
                
                hop_data = {
                    "from_address": from_addr,
                    "to_address": to_addr,
                    "amount": str(event.args["value"] / 1e6),
                    "contract_type": classify_address(from_addr),
                    "hop_number": hop + 1,
                    "tx_hash": event.transactionHash.hex()
                }
                all_hops.append(hop_data)
                
                if hop + 1 < max_hops:
                    queue.append((from_addr, hop + 1, to_addr, hop_data["contract_type"]))
        except Exception:
            continue
    
    return all_hops
```

**Source:** Used in `src/data/onchain_client.py:152-187`.

---

### Get Transaction Receipt

Get full transaction receipt with logs.

```python
tx_hash = "0xabc123..."

# Get transaction
tx = w3.eth.get_transaction(tx_hash)

# Get receipt
receipt = w3.eth.get_transaction_receipt(tx_hash)

print(f"Status: {receipt['status']}")  # 1 = success
print(f"Gas used: {receipt['gasUsed']}")
print(f"Block: {receipt['blockNumber']}")

# Parse logs
for log in receipt["logs"]:
    print(f"Contract: {log['address']}")
    print(f"Topics: {[t.hex() for t in log['topics']]}")
```

---

### Get Transaction Trace (Debug)

Get detailed trace of a transaction (requires debug-enabled node).

```python
# Using Alchemy
result = w3.provider.make_request(
    "debug_traceTransaction",
    [tx_hash, {"tracer": "callTracer"}]
)

# Parse call trace
calls = result["calls"]
for call in calls:
    print(f"Type: {call['type']}")
    print(f"From: {call['from']}")
    print(f"To: {call['to']}")
    print(f"Value: {call.get('value')}")
```

---

### Check if Address is Contract

```python
def is_contract(w3, address):
    """Check if address is a contract (not EOA)."""
    address = w3.to_checksum_address(address)
    code = w3.eth.get_code(address)
    return len(code) > 2
```

---

### Classify Address (Mixer/Bridge/Contract)

```python
MIXER_CONTRACTS = {
    "tornado_cash": ["0x91031bCf8b7a6282b7a8403f46B4a7c9B6B0555D", ...],
    "railgun": ["0x19G7cF2D8b4E3f6A2c5D8A1b6F9E3D5C7A2B4E6D", ...],
}

BRIDGE_CONTRACTS = {
    "multichain": ["0xC564EE9f21c8C733732019Ca51bb6FA18EdA78A5", ...],
    "stargate": ["0xdf0770dF86a8034b3EFEf0A1Bb3c889B8332FF56", ...],
    "layerzero": ["0xb6319cC6E9650A86F0cD1c817AbC76C91F9c5d4E", ...],
}

def classify_address(w3, address):
    """Classify what type of address this is."""
    address = address.lower()
    
    # Check if contract
    if is_contract(w3, address):
        # Check mixers
        for mixer, addrs in MIXER_CONTRACTS.items():
            if address in [a.lower() for a in addrs]:
                return f"mixer:{mixer}"
        
        # Check bridges
        for bridge, addrs in BRIDGE_CONTRACTS.items():
            if address in [a.lower() for a in addrs]:
                return f"bridge:{bridge}"
        
        return "unknown_contract"
    
    return "wallet"
```

---

### Get Token Balance (ERC-20)

```python
def get_token_balance(w3, wallet, token_address):
    """Get ERC-20 token balance for a wallet."""
    
    # Minimal ERC-20 ABI
    abi = [
        {
            "name": "balanceOf",
            "type": "function",
            "inputs": [{"name": "owner", "type": "address"}],
            "outputs": [{"name": "", "type": "uint256"}]
        }
    ]
    
    token = w3.eth.contract(
        address=w3.to_checksum_address(token_address),
        abi=abi
    )
    
    balance = token.functions.balanceOf(wallet).call()
    return balance
```

---

### Get Multiple Token Balances

```python
def get_portfolio(w3, wallet):
    """Get full portfolio for a wallet."""
    tokens = {
        "USDC": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa841174",
        "USDT": "0xc2132D05D013c5EF71C41ED0E4aD4B70F5d9a5b6",
        "WMATIC": "0x0d500B1d8eFAEF0deC5C1651cD344CAb5E3de002",
    }
    
    portfolio = {}
    for name, address in tokens.items():
        balance = get_token_balance(w3, wallet, address)
        portfolio[name] = balance
    
    # Add MATIC
    portfolio["MATIC"] = w3.eth.get_balance(wallet)
    
    return portfolio
```

---

### Get Events for Address

```python
def get_events_for_address(w3, address, contract_address, event_name="Transfer"):
    """Get all events of a specific type for an address."""
    
    contract = w3.eth.contract(
        address=w3.to_checksum_address(contract_address)
    )
    
    # Get incoming
    incoming_filter = contract.events[event_name].create_filter(
        from_block=0,
        to_block="latest",
        argument_filters={"to": address}
    )
    
    incoming = []
    for event in incoming_filter.get_all_entries():
        incoming.append({
            "from": event.args["from"],
            "to": event.args["to"],
            "value": event.args["value"],
            "block": event.blockNumber,
            "tx": event.transactionHash.hex()
        })
    
    # Get outgoing
    outgoing_filter = contract.events[event_name].create_filter(
        from_block=0,
        to_block="latest",
        argument_filters={"from": address}
    )
    
    outgoing = []
    for event in outgoing_filter.get_all_entries():
        outgoing.append({
            "from": event.args["from"],
            "to": event.args["to"],
            "value": event.args["value"],
            "block": event.blockNumber,
            "tx": event.transactionHash.hex()
        })
    
    return {"incoming": incoming, "outgoing": outgoing}
```

---

## ERROR HANDLING

### Status Codes

| Code | Meaning |
|------|---------|
| -32000 | Invalid input |
| -32001 | Gas limit exceeded |
| -32002 | Unknown chain |

### Connection Errors

```python
if not w3.is_connected():
    raise ConnectionError("Not connected to Polygon RPC")

# Test connection
try:
    block = w3.eth.block_number
except Exception as e:
    print(f"Error: {e}")
```

---

## PYTHON CLIENT WRAPPER

From `src/data/onchain_client.py`:

```python
class OnchainClient:
    def __init__(self, rpc_url: str = None):
        settings = get_settings()
        self.rpc_url = rpc_url or settings.polygon_rpc_url
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        if not self.w3.is_connected():
            logger.warning("Could not connect to Polygon RPC")
        
        self.usdc_contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(USDC_CONTRACTS["polygon"]),
            abi=self._get_usdc_abi()
        )
    
    def get_usdc_transfers(self, address: str, from_block: int = 0, to_block: str = "latest"):
        address = self.w3.to_checksum_address(address)
        
        Transfer = self.usdc_contract.events.Transfer
        
        # Incoming
        incoming_filter = Transfer.create_filter(
            from_block=from_block,
            to_block=to_block,
            argument_filters={"to": address}
        )
        
        incoming = []
        for event in incoming_filter.get_all_entries():
            incoming.append({
                "from": event.args["from"],
                "to": event.args["to"],
                "value": event.args["value"] / 1e6,
                "block_number": event.blockNumber,
                "tx_hash": event.transactionHash.hex(),
            })
        
        return {"incoming": incoming, "outgoing": []}
    
    def trace_fund_origin(self, address: str, max_hops: int = 5):
        all_hops = []
        visited = set()
        queue = [(address.lower(), 0, None, "wallet")]
        
        while queue and len(all_hops) < 100:
            current_addr, hop, prev_addr, contract_type = queue.pop(0)
            
            if current_addr in visited or hop >= max_hops:
                continue
            visited.add(current_addr)
            
            transfers = self.get_usdc_transfers(current_addr)
            
            for transfer in transfers["incoming"]:
                hop_data = {
                    "from_address": transfer["from"].lower(),
                    "to_address": transfer["to"].lower(),
                    "amount": str(transfer["value"]),
                    "contract_type": self._classify_address(transfer["from"]),
                    "tx_hash": transfer["tx_hash"]
                }
                all_hops.append(hop_data)
                
                if hop + 1 < max_hops:
                    queue.append((transfer["from"].lower(), hop + 1, transfer["to"], hop_data["contract_type"]))
        
        return all_hops
    
    def is_contract(self, address: str) -> bool:
        code = self.w3.eth.get_code(w3.to_checksum_address(address))
        return len(code) > 2
    
    def get_transaction_trace(self, tx_hash: str) -> Dict:
        tx = self.w3.eth.get_transaction(tx_hash)
        receipt = self.w3.eth.get_transaction_receipt(tx_hash)
        
        return {
            "hash": tx_hash,
            "from": tx["from"],
            "to": tx["to"],
            "value": tx["value"],
            "gas_used": receipt["gasUsed"],
            "status": receipt["status"],
            "logs": receipt["logs"]
        }
```

---

## CHAIN INFORMATION

| Property | Value |
|----------|-------|
| Chain ID | 137 |
| Chain Name | Polygon PoS |
| Block Time | ~2 seconds |
| Explorer | polygonscan.com |

---

## QUICK REFERENCE

| Method | Web3 Call | Use |
|--------|-----------|-----|
| Latest block | `w3.eth.block_number` | Get current block |
| Wallet balance | `w3.eth.get_balance(addr)` | Get MATIC balance |
| Token balance | `contract.functions.balanceOf(addr).call()` | Get ERC-20 balance |
| Nonce | `w3.eth.get_transaction_count(addr)` | Get transaction count |
| Is contract | `w3.eth.get_code(addr)` | Check if contract |
| Transaction receipt | `w3.eth.get_transaction_receipt(hash)` | Get tx details |
| Event logs | `contract.events.Transfer.get_logs()` | Get transfer events |

---

## SEE ALSO

- [Crypto Basics](../01_crypto/)
- [Quick Reference](_endpoints.md)
- [Alchemy API](alchemy.md)
- Source: `src/data/onchain_client.py`