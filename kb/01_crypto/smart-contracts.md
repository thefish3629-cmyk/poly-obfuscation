# Smart Contracts

Self-executing code on blockchain.

## Basics

- Deployed at an address
- Call methods via transaction
- State changes are permanent
- Gas fees pay for execution

## Deployment (Polygon)

```bash
# Using Hardhat
npx hardhat run scripts/deploy.js --network polygon

# Using Foundry
forge create --rpc-url $POLYGON_RPC --private-key $PRIVATE_KEY
```

## Interacting

### web3.py
```python
from web3 import Web3
w3 = Web3(Web3.HTTPProvider(POLYGON_RPC))

contract = w3.eth.contract(address=ADDRESS, abi=ABI)
result = contract.functions.methodName().call()
```

### ethers.js
```javascript
const contract = new ethers.Contract(address, abi, provider);
const result = await contract.methodName();
```

## Gas

- Gas limit: max gas for transaction
- Gas price: gwei paid per unit gas
- Total = gas limit * gas price

### Estimate Gas
```python
gas_estimate = contract.functions.methodName().estimateGas({'from': wallet})
```

## Common Contracts on Polygon

| Contract | Address |
|----------|---------|
| Polygon PoS Bridge | 0x401E6C73FC752F6aE3e3f3B4b2f8eBF9C81eF6a7 |
| Plasma Child Chain | 0x7585317B6eB7e452110C5603e4f7baC0cD3D5deB |
| ERC20 Predicate | 0x2e985DadA63fbE25D3e13C7fC1fBD53E4F6C3D7 |

## Security

- Reentrancy guards
- Check-effects-interaction pattern
- Pull over push (withdraw pattern)
- Use libraries (OpenZeppelin)

## See Also

- [Polygon RPC](../02_apis/polygon-rpc.md)
- [Detection Methods](../04_analysis/detection-methods.md)