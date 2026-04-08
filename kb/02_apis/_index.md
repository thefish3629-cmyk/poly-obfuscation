# 02_apis - API References

Complete API documentation for all data sources.

## APIs Overview

| API | Description | Source |
|----|-------------|--------|
| [Polymarket](polymarket.md) | Markets, trades, positions, order book | `src/data/api_clients.py` |
| [Dune](dune.md) | SQL queries on blockchain data | `src/data/dune_client.py` |
| [Goldsky](goldsky.md) | GraphQL subgraphs | `src/data/subgraph_client.py` |
| [Polygon RPC](polygon-rpc.md) | On-chain data, events | `src/data/onchain_client.py` |
| [Alchemy](alchemy.md) | Enhanced Polygon access | `src/data/onchain_client.py` |

## Quick Start

### Environment Variables

```bash
# Required
POLYGON_RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY
DUNE_API_KEY=YOUR_DUNE_KEY

# Optional
GOLDSKY_API_KEY=YOUR_GOLDSKY_KEY
```

## Authentication

| API | Auth Method |
|-----|------------|
| Polymarket | None (public) |
| Dune | Header `x-dune-api-key` |
| Goldsky | Header `x-api-key` (optional) |
| Polygon/Alchemy | API key in URL |

## Rate Limits

| API | Free Tier | Recommended |
|-----|----------|------------|
| Polymarket | 10 req/sec | Cache responses |
| Dune | 10/day | Upgrade to Pro |
| Goldsky | 10K/day | Use pagination |
| Polygon RPC | ~5/sec | Use Alchemy |

## Common Workflows

1. **Get Market** → Polymarket Gamma API
2. **Get Trades** → Polymarket Data API OR Dune
3. **Get User Balances** → Goldsky Positions API
4. **Trace Funds** → Polygon RPC (Alchemy)
5. **Get Historical** → Dune Analytics

## Quick Reference

See [_endpoints.md](_endpoints.md) for all endpoints in one file.

## Error Handling

Each API doc includes:
- Status codes
- Retry logic
- Fallback strategies

## See Also

- [Polymarket Platform Docs](../03_polymarket/)
- [Crypto Basics](../01_crypto/)
- [Detection Methods](../04_analysis/detection-methods.md)