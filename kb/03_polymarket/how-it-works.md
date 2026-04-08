# How Polymarket Works

Prediction market platform on Polygon.

## Core Concepts

### Binary Outcomes

Every market has exactly two outcomes:
- **YES** - pays $1 if outcome occurs
- **NO** - pays $1 if outcome doesn't occur

Prices represent probability (0-100%).

### CLOB (Central Limit Order Book)

Unlike most prediction markets (which use AMM), Polymarket uses a real order book.

- Makers place orders at specific prices
- Takers fill existing orders
- Spread = difference between best bid/ask

### Token Structure

Each outcome is an ERC-721 token.

```
Market: "Will X happen?"
├── YES token (e.g., "t-123-yes")
└── NO token (e.g., "t-123-no")
```

A "YES" and "NO" together always resolve to $1.

## Trading Flow

```
1. Find market (via API or search)
2. Get CLOB token IDs
3. Get order book
4. Place order (limit) or take (market)
5. Verify transaction on Polygon
```

## Liquidity

- No spread baked in (unlike AMM)
- Makers provide liquidity
- 0% platform fee
- Taker fees: ~0.25% (maker rebates)

## Settlement

When market resolves:
- Winning tokens pay $1 each
- Losing tokens worth $0
- Unresolved = can trade indefinitely

## Resolution

Markets resolve based on real-world events.

Sources:
- News (70%+ credibility)
- Official sources
- Oracle decisions

## Contract Addresses (Polygon)

| Contract | Address |
|----------|---------|
| CLOB | 0x4bFb41d... (proxy) |
| Token ATC | 0x1e541... |

## Key Features

| Feature | Description |
|---------|-------------|
| No KYC | No identity required |
| 0% fees | Platform free |
| USDC only | Single collateral |
| On-chain | All trades recorded |
| Telegram | Integrated discussion |

## Why CLOB Over AMM

| CLOB | AMM |
|------|-----|
| Prices discovered | 50/50 in, fixed curve |
| Maker rebates | Impermanent loss |
| Spread determined by market | Spread baked in |
| More price discovery | Less efficient |

## History

Polymarket was originally:
- 2020: Fixed odds betting
- 2022: Switched to CLOB model
- 2024: Became largest prediction market

## See Also

- [Trading Guide](trading.md)
- [Markets](markets.md)
- [API Docs](../02_apis/polymarket.md)