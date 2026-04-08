# Polymarket Markets

Understanding and finding markets.

## Market Structure

Each market has:

| Field | Description |
|-------|-------------|
| conditionId | Unique identifier |
| question | Market question |
| slug | URL-friendly name |
| clobTokenIds | [YES_id, NO_id] |
| volume | Total volume ($) |
| closed | Resolved or not |

## Finding Markets

### 1. Search API

```python
import requests

response = requests.get(
    "https://gamma.polymarket.com/markets",
    params={"question": "iran", "limit": 10}
)
markets = response.json()
```

### 2. Public Search

```
https://polymarket.com/search?q=iran
```

### 3. Browse Categories

- Politics
- Science
- Economics
- Sports
- Crypto

## Market States

### Active

- Trading open
- Not resolved yet
- Volume accumulates

### Closed

- Market resolved
- Winners paid
- No more trading

### Traded

- Resolved but disputed
- Under review

## Reading a Market

```
Will [X] happen by [date]?

YES @ $0.65 (65% chance)
NO @ $0.35 (35% chance)

Volume: $1.5M
Liquidity: $500K
```

**Price = implied probability**

- YES @ $0.65 = 65% chance
- NO @ $0.35 = 35% chance

## Market Analysis

### Volume

Total $ traded. Higher = more interest.

### Liquidity

Depth in order book. Higher = easier to trade.

### Spread

Bid-ask difference. Tight = efficient pricing.

### Accuracy

Historical vs resolved. Good markets ~75%+ accurate.

## Categories

### Politics
- Elections
- Geopolitics
- Policy

### Science
- Space
- Medical
- Technology

### Economics
- Fed decisions
- Recession
- Inflation

### Crypto
- BTC price
- ETF approval
- Regulation

## Notable Markets

### Iran-Israel

"Will Israel strike Iranian nuclear facility before July?"

- High volume
- Geopolitical tension
- Resolved July 2025

### US Election

"Who will win 2024 US Presidential election?"

- Highest volume
- November resolution

## Creating Markets

Not available to public yet.

- Apply via Polymarket
- Must verify need
- Provide resolution source

## Market Resolution

1. Source reports outcome
2. Admin reviews
3. Market resolves
4. Tokens settle

Sources for resolution:
- Major news (70%+ credibility)
- Official government
- Designated oracles

## See Also

- [How It Works](how-it-works.md)
- [Trading](trading.md)
- [API Docs](../02_apis/polymarket.md)