# On-Chain Analysis

Analyzing blockchain data.

## Data Sources

### RPC Nodes
- Read contract state
- Get blocks, transactions, traces
- Example: Alchemy, Infura, Polygon RPC

### Block Explorers
- Polygon: [polygonscan.com](https://polygonscan.com)
- Etherscan (mainnet), Arbiscan, etc.

### Analytics Platforms
- [Dune](https://dune.com)
- [Goldsky](https://goldsky.com)
- [Dune API](../02_apis/dune.md)

## Key Metrics

### Wallet Analysis
- Transaction count
- Total volume (ETH/token)
- First/last activity
- Gas spent

### Contract Analysis
- Total calls
- Unique callers
- Function selector usage

### Network Analysis
- Token transfers between addresses
- Common patterns
- Cluster analysis

## Common Queries

### Get Wallet Transactions
```python
# Via Polygon RPC
txs = w3.eth.get_account_transactions(address)
```

### Get Contract Events
```python
# Via web3.py
contract = w3.eth.contract(address=CONTRACT, abi=ABI)
events = contract.events.Transfer.getLogs(fromBlock=1, toBlock='latest')
```

## Tools

| Tool | Use |
|------|-----|
| web3.py | Direct RPC calls |
| ethers.js | JavaScript RPC |
| Dune | SQL on-chain queries |
| Goldsky | Subgraphs |
| Tenderly | Simulation/debug |

## Tracing

### Debug Trace
Polygon supports debug_traceTransaction:
```python
result = w3.provider.make_request(
    "debug_traceTransaction",
    [tx_hash, {"tracer": "callTracer"}]
)
```

## See Also

- [Polygon RPC](../02_apis/polygon-rpc.md)
- [Dune API](../02_apis/dune.md)
- [Detection Methods](../04_analysis/detection-methods.md)