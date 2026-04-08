# Token Standards

## ERC-20

Fungible token standard (fungible = interchangeable).

```solidity
interface IERC20 {
    function transfer(address to, uint256 amount) returns (bool);
    function balanceOf(address account) view returns (uint256);
    function approve(address spender, uint256 amount) returns (bool);
    function allowance(address owner, address spender) view returns (uint256);
}
```

### Common ERC-20 on Polygon
| Token | Symbol | Address |
|-------|--------|---------|
| Tether | USDT | 0xc2132D05D013c5EF71C41ED0E4aD4B70F5d9a5b6 |
| USD Coin | USDC | 0x2791Bca1f2de4661ED88A30C99A7a9449Aa841174 |
| Wrapped Matic | WMATIC | 0x0d500B1d8eFAEF0deC5C1651cD344CAb5E3de002 |

## ERC-721

Non-fungible token (NFT).

```solidity
interface IERC721 {
    function ownerOf(uint256 tokenId) view returns (address);
    function transferFrom(address from, address to, uint256 tokenId);
    function safeTransferFrom(address from, address to, uint256 tokenId);
}
```

## ERC-1155

Multi-token standard (both fungible and non-fungible).

## Token Transfers

### ERC-20 Transfer
1. Approve contract to spend your tokens
2. Call `transferFrom` or have contract call `transfer`

### ETH native transfer
```solidity
payable(recipient).transfer(amount);
```

### ERC-721 Transfer
- `transferFrom`: unsafe (no callback)
- `safeTransferFrom`: safe (calls `onERC721Received`)

## Wrapped Tokens

- WETH: Wrapped ETH (ERC-20 interface for ETH)
- WMATIC: Wrapped MATIC
- Wrap via contract: deposit ETH, receive WETH

## See Also

- [Polymarket API](../02_apis/polymarket.md)
- [Smart Contracts](smart-contracts.md)