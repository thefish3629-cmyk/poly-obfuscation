# CLOB Token IDs

Understanding token identifiers on Polymarket.

## What are Token IDs

Each market outcome is an ERC-721 token.

```
Market: "Will X happen?"
├── YES token: "t-12345-yes"
└── NO token: "t-12345-no"
```

## Token ID Format

```
t-{market_id}-{outcome}

t-12345-yes
t-12345-no
```

Where:
- `t-` = prefix
- `market_id` = numeric or slug
- `outcome` = "yes" or "no"

## Getting Token IDs

### From API

```python
import requests

response = requests.get(
    "https://gamma.polymarket.com/markets",
    params={"question": "Israel Iran nuclear"}
)
market = response.json()[0]
token_ids = market["clobTokenIds"]

yes_token = token_ids[0]  # First = YES
no_token = token_ids[1]   # Second = NO
```

### Response

```json
{
  "conditionId": "abc123",
  "question": "Will Israel strike...?",
  "clobTokenIds": [
    "t-123-yes",
    "t-123-no"
  ]
}
```

## Using Token IDs

### Order Book

```python
token_id = "t-123-yes"

response = requests.get(
    f"https://clob.polymarket.com/order-book/{token_id}"
)
book = response.json()

# Best bid/ask
best_bid = book["bids"][0][0]  # Price
best_ask = book["asks"][0][0]
```

### Price History

```python
response = requests.get(
    "https://clob.polymarket.com/prices-history",
    params={"token_id": "t-123-yes", "interval": "1h"}
)
prices = response.json()
```

### Get Trades

```python
response = requests.get(
    "https://data-api.polymarket.com/trades",
    params={"market": condition_id}
)
```

## Token Lifecycle

1. **Created**: Market goes live
2. **Trading**: Tokens transferable
3. **Resolved**:
   - Winner pays $1
   - Loser worth $0 (can keep as souvenir)

## Trading with Token IDs

### Buying YES

1. Get YES token ID from market
2. Call buy function in CLOB contract
3. Specify amount and limit price
4. Pay in USDC

### Selling

1. Have YES or NO token (ERC-721)
2. Call sell function
3. Receive USDC

## Contract Details

### ERC-721 Interface

```solidity
// Transfer token
safeTransferFrom(
    from,
    to,
    tokenId,
    amount,  // always 1 for binary
    data
);

// Check balance
balanceOf(owner, tokenId);
```

### CLOB Contract

Handles:
- Order placement
- Order matching
- Settlement on resolution

## Common Token IDs

| Market | YES Token | NO Token |
|--------|-----------|----------|
| Iran-Israel nuclear | t-xxx-yes | t-xxx-no |
| US Election | t-yyy-yes | t-yyy-no |

(Replace xxx/yyy with actual IDs from API)

## Price Decimal

Prices in cents:
- 65 = $0.65
- 100 = $1.00
- 35 = $0.35

## Notes

- Both tokens together = $1 (always)
- Price sums to $1 (with rounding)
- Only winning side worth anything at resolution

## See Also

- [How It Works](how-it-works.md)
- [Trading](trading.md)
- [API Docs](../02_apis/polymarket.md)