# API Endpoints Quick Reference

All endpoints in one place.

## Polymarket

| Endpoint | Method | URL |
|----------|--------|-----|
| Search markets | GET | `https://gamma.polymarket.com/markets?question=...` |
| Market by ID | GET | `https://gamma.polymarket.com/markets/{id}` |
| Trades | GET | `https://data-api.polymarket.com/trades?market=...` |
| Positions | GET | `https://data-api.polymarket.com/positions?user=...` |
| Activity | GET | `https://data-api.polymarket.com/activity?user=...` |
| Order book | GET | `https://clob.polymarket.com/order-book/{token}` |
| Price history | GET | `https://clob.polymarket.com/prices-history?token_id=...` |
| Fallback search | GET | `https://api.polymarket.com/markets?question=...` |

## Dune

| Endpoint | Method | URL |
|----------|--------|-----|
| Execute query | POST | `https://api.dune.com/api/v1/query/{id}/execute` |
| Check status | GET | `https://api.dune.com/api/v1/execution/{exec_id}/status` |
| Get results | GET | `https://api.dune.com/api/v1/execution/{exec_id}/results` |

Headers: `x-dune-api-key: YOUR_KEY`

## Goldsky

| Endpoint | Method | URL |
|----------|--------|-----|
| GraphQL | POST | `https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/graphql` |

## Polygon RPC

| Method | Web3 Call |
|--------|-----------|
| Latest block | `w3.eth.block_number` |
| Get balance | `w3.eth.get_balance(address)` |
| Get nonce | `w3.eth.get_transaction_count(address)` |
| Get code | `w3.eth.get_code(address)` |
| Call contract | `w3.eth.call({to, data})` |
| Send tx | `w3.eth.send_transaction({to, from, value})` |
| Gas price | `w3.eth.gas_price` |

Base URL: `https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY`

## Quick Curl Examples

### Polymarket Search
```bash
curl "https://gamma.polymarket.com/markets?question=iran&limit=5"
```

### Dune Execute
```bash
curl -X POST "https://api.dune.com/api/v1/query/2435483/execute" \
  -H "x-dune-api-key: YOUR_KEY"
```

### Dune Status
```bash
curl "https://api.dune.com/api/v1/execution/EXEC_ID/status" \
  -H "x-dune-api-key: YOUR_KEY"
```

### Polygon Balance
```bash
curl -X POST "https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_getBalance","params":["ADDRESS","latest"],"id":1}'
```

## Environment Variables

```
# .env
POLYGON_RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY
DUNE_API_KEY=YOUR_DUNE_KEY
GOLDSKY_API_KEY=YOUR_GOLDSKY_KEY
```

## See Also

- [Polymarket API](polymarket.md)
- [Dune API](dune.md)
- [Goldsky API](goldsky.md)
- [Polygon RPC](polygon-rpc.md)