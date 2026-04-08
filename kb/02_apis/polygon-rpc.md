# Polygon RPC

Polygon PoS node API for reading/writing to the chain.

## Base URLs

### Public (Rate Limited)
```
https://polygon-rpc.com
https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY
```

### Alchemy (Recommended)
```
https://polygon-mainnet.g.alchemy.com/v2/YOUR_API_KEY
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

Or in headers (web3.py):
```python
from web3 import Web3

w3 = Web3(Web3.HTTPProvider(
    "https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY"
))
```

## Common Methods

### eth_blockNumber

Get latest block number.

```python
block = w3.eth.block_number
```

### eth_getBalance

Get wallet balance.

```python
balance = w3.eth.get_balance(wallet_address)
# Returns in wei
```

### eth_getTransactionCount

Get nonce for address.

```python
nonce = w3.eth.get_transaction_count(wallet_address)
```

### eth_getCode

Get contract bytecode.

```python
code = w3.eth.get_code(contract_address)
# Returns "0x" if EOA
```

### eth_call

Read contract state (no gas).

```python
result = w3.eth.call({
    'to': contract_address,
    'data': encoded_data
})
```

### eth_sendTransaction

Send transaction (requires signing).

```python
tx_hash = w3.eth.send_transaction({
    'to': recipient,
    'from': sender,
    'value': amount_wei
})
```

## web3.py Example

```python
from web3 import Web3

w3 = Web3(Web3.HTTPProvider(
    "https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY"
))

# Check connection
print(w3.is_connected())  # True/False

# Get latest block
block = w3.eth.block_number
print(f"Latest block: {block}")

# Get wallet balance
balance = w3.eth.get_balance("0x123...")
print(f"Balance: {w3.from_wei(balance, 'matic')} MATIC")
```

## Chain ID

- Polygon: 137
- Mumbai (testnet): 80001

## Block Explorer

- Mainnet: [polygonscan.com](https://polygonscan.com)
- Mumbai: [mumbai.polygonscan.com](https://mumbai.polygonscan.com)

## Gas Prices

```python
# Get current gas price
gas_price = w3.eth.gas_price
print(f"Gas: {w3.from_wei(gas_price, 'gwei')} gwei")
```

### Gas Oracle (EIP-1559)

```python
oracle = w3.eth.gas_oracle()
print(oracle)
# {'lastBlock': ..., 'suggestedBaseFee': ..., 'gasPrice': ...}
```

## Common Contracts (Polygon)

| Contract | Address |
|----------|---------|
| MATIC | 0x0000... (native) |
| USDC | 0x2791Bca1f2de4661ED88A30C99A7a9449Aa841174 |
| USDT | 0xc2132D05D013c5EF71C41ED0E4aD4B70F5d9a5b6 |

## Reading ERC-20 Balances

```python
from web3 import Web3

w3 = Web3(Web3.HTTPProvider(RPC_URL))

# USDC contract
USDC = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa841174"
ABI = "[{\"name\":\"balanceOf\",\"type\":\"function\",\"inputs\":[{\"name\":\"owner\",\"type\":\"address\"}],\"outputs\":[{\"name\":\"\",\"type\":\"uint256\"}]}]"

contract = w3.eth.contract(address=USDC, abi=ABI)
balance = contract.functions.balanceOf(wallet).call()
print(balance / 1e6)  # USDC has 6 decimals
```

## Debug Methods

### debug_traceTransaction

Trace a transaction (requires debug enabled node).

```python
result = w3.provider.make_request(
    "debug_traceTransaction",
    [tx_hash, {"tracer": "callTracer"}]
)
```

## Errors

| Code | Meaning |
|------|---------|
| -32000 | Invalid input |
| -32001 | Gas limit exceeded |
| -32002 | Unknown chain |

## See Also

- [Crypto Basics](../01_crypto/)
- [Quick Reference](_endpoints.md)
- [Source Code](../../src/data/onchain_client.py)