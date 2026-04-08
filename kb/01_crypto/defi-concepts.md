# DeFi Concepts

Decentralized Finance fundamentals.

## AMM (Automated Market Maker)

Trading mechanism using liquidity pools instead of order books.

- Traders swapToken A for Token B
- Price determined by constant product formula: `x * y = k`
- Liquidity providers earn fees

## Liquidity Pools

Smart contracts holding two or more tokens.

| Pool Type | Example |
|----------|---------|
| Stable | USDC/USDT |
| Correlated | ETH/stETH |
| Uncorrelated | ETH/MATIC |

## Yield Farming

Earning yield by providing liquidity.

- APY: Annual Percentage Yield (compound interest)
- APR: Annual Percentage Rate (simple interest)

## Impermanent Loss

Value loss when providing liquidity vs holding.

- Occurs when token prices diverge
- Higher volatility = higher impermanent loss
- Mitigated by stable pairs

## Common DeFi Protocols

| Protocol | Type | Chain |
|----------|------|-------|
| Uniswap | AMM | Ethereum |
| Aave | Lending | Multi |
| Curve | Stable AMM | Ethereum |
|Balancer| AMM | Multi |

## See Also

- [Tokens](tokens.md)
- [Mixer Detection](../04_analysis/detection-methods.md)