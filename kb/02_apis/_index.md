# 02_apis - API References

API documentation for crypto platforms.

## Topics

- [polymarket.md](polymarket.md) - Gamma, CLOB, Data APIs
- [dune.md](dune.md) - Query execution API
- [goldsky.md](goldsky.md) - Subgraph API
- [polygon-rpc.md](polygon-rpc.md) - Polygon RPC
- [_endpoints.md](_endpoints.md) - Quick reference

## Authentication

| API | Auth Method |
|-----|------------|
| Polymarket | None (public) |
| Dune | Header `x-dune-api-key` |
| Goldsky | Header `x-api-key` |
| Polygon RPC | API key in URL |
| Alchemy | API key in URL |

## Quick Reference

See [_endpoints.md](_endpoints.md) for all endpoints at a glance.

## Common Patterns

### Dune Query Flow
1. Execute query → get execution_id
2. Poll status endpoint
3. Fetch results

### Polymarket Flow
1. Get market by slug/question
2. Get CLOB token IDs
3. Fetch trades/positions

## Rate Limits

| API | Limit |
|-----|-------|
| Polymarket Gamma | ~10 req/sec |
| Dune | Plan-based |
| Goldsky | Plan-based |
| Polygon RPC | Plan-based |

## See Also

- [Polymarket Platform Docs](../03_polymarket/)
- [Current Project](../05_projects/current-project.md)