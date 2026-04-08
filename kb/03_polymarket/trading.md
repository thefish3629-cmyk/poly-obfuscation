# Trading on Polymarket

How to trade on the platform.

## Prerequisites

1. **Wallet**: MetaMask or compatible
2. **USDC**: On Polygon network
3. **Bridge**: If on Ethereum mainnet

## Funding Account

### Get USDC on Polygon

1. Buy USDC on exchange (Coinbase, Binance)
2. Bridge to Polygon:
   - Use [Polygon Bridge](https://bridge.polygon.technology/)
   - Or [Jumper.exchange](https://jumper.exchange/)

### Deposit to Polymarket

No explicit deposit. Just send USDC to the CLOB contract.

- Send USDC to: (check official docs for current address)
- Approved automatically on first trade

## Placing Trades

### Via Web Interface

1. Go to [polymarket.com](https://polymarket.com)
2. Search for market
3. Select position (YES/NO)
4. Enter amount
5. Choose: Market (instant) or Limit (your price)
6. Confirm in wallet

### Via API

```python
import requests

# 1. Get market
market_resp = requests.get(
    "https://gamma.polymarket.com/markets",
    params={"question": "Will Iran strike Israel?"}
)
market = market_resp.json()[0]
token_id = market["clobTokenIds"][0]  # YES token

# 2. Get order book
book_resp = requests.get(
    f"https://clob.polymarket.com/order-book/{token_id}"
)
book = book_resp.json()
print(f"Bid: {book['bids'][0][0]}, Ask: {book['asks'][0][0]}")

# 3. Place order (via smart contract)
# See contract calls in CLOB contract
```

## Order Types

### Market Order

Take existing price immediately.

- Pays spread + fee
- Instant execution
- Uncertain price

### Limit Order

Set your price.

- Only executes if reached
- No obligation
- May not fill

## Fees

| Type | Fee |
|------|-----|
| Taker | ~0.25% |
| Maker | -0.05% (rebate) |

Minimum trade: $0.01

## Contract Interaction

### Wrap USDC (for approvals)

```solidity
// Approve CLOB to spend USDC
usdc.approve(clobAddress, amount);
```

### Place Order

```solidity
// Place limit order
clob.placeOrder(
    tokenId,
    amount,
    price,  // in cents (e.g., 65 = $0.65)
    side   // 0 = buy, 1 = sell
);
```

### Cancel Order

```solidity
clob.cancelOrder(orderId);
```

## Gas Fees

Polygon has low gas (~0.001-0.01 MATIC per trade).

- Check [gas tracker](https://polygonscan.com/gastracker)
- Use suggest gas for faster confirmation

## Tips

1. **Use limit orders** - avoid slippage
2. **Check depth** - large orders move price
3. **Watch spread** - tight = liquid, wide = illiquid
4. **No KYC** - trade freely

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Transaction failed | Increase gas |
| Order won't fill | Price too far from bid/ask |
| USDC not showing | Add USDC to wallet |

## See Also

- [How It Works](how-it-works.md)
- [Markets](markets.md)
- [API Docs](../02_apis/polymarket.md)