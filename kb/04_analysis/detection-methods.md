# Detection Methods

Algorithms for detecting obfuscation on Polymarket.

## Overview

| Detection Type | Target | Confidence |
|----------------|--------|------------|
| Mixer | Tornado Cash, Railgun, Aztec | 85-95% |
| Bridge | Multi-chain, LayerZero | 70-85% |
| Sybil | Clustered wallets | 60-80% |
| Layering | Multi-hop flows | 75-85% |

---

## Mixer Detection

Identifies trades funded via mixers.

### Known Mixers

| Mixer | Chain | Addresses |
|-------|-------|----------|
| Tornado Cash | Ethereum | 0xdef..., 0x905... |
| Railgun | Polygon | 0xebbc... |
| Aztec | Ethereum | 0x237... |

### Methods

#### 1. Direct Interaction

Check if wallet directly interacted with mixer contract.

```python
transfers = onchain.get_usdc_transfers(wallet)
for transfer in transfers["incoming"] + transfers["outgoing"]:
    if transfer["to"] in MIXER_CONTRACTS:
        return {"mixer_type": "...", "confidence": 95%}
```

**Confidence**: 95% (definitive)

#### 2. Funding Trace

Trace origin of funds through hops.

```python
hops = onchain.trace_fund_origin(wallet, max_hops=3)
mixer_hops = [h for h in hops if h.startswith("mixer")]
```

**Confidence**: 70-85%

#### 3. Heuristics

| Heuristic | Pattern | Confidence |
|-----------|---------|------------|
| Timing | Regular intervals | 60% |
| Denomination | Fixed amounts (0.1, 1, 10, 100) | 75% |
| Gas fingerprint | Same gas across txs | 80% |

### Implementation

Source: `src/detection/mixers.py`

---

## Bridge Detection

Tracks cross-chain fund flows.

### Known Bridges

| Bridge | Chain | Addresses |
|--------|-------|----------|
| Multichain | Multi | 0xb31f... |
| Stargate | Multi | 0x65c6... |
| LayerZero | Multi | 0x000a... |
| Wormhole | Multi | 0x3ee1... |
| Polygon Bridge | Polygon | 0x401E... |

### Methods

#### 1. Direct Bridge Interaction

```python
transfers = onchain.get_usdc_transfers(wallet)
for transfer in transfers:
    if transfer["to"] in BRIDGE_CONTRACTS:
        return {"bridge_type": "...", "confidence": 85%}
```

#### 2. Chain Hopping Pattern

Multiple bridges in short succession.

```python
bridges_used = []
for hop in hops:
    if hop["type"] == "bridge":
        bridges_used.append(hop["bridge"])
if len(bridges_used) >= 2:
    return {"chain_hopping": True, "confidence": 70%}
```

### Implementation

Source: `src/detection/bridges.py`

---

## Sybil Detection

Clusters wallets controlled by same entity.

### Methods

#### 1. Common Funding Source

Multiple wallets funded from same source.

```python
source = trace_fund_origin(wallet1)
if source == trace_fund_origin(wallet2):
    return {"cluster": True, "confidence": 80%}
```

#### 2. Trading Patterns

Same behavior across wallets.

- Similar timing
- Same market preferences
- Coordinated amounts

#### 3. Network Analysis

Graph of transactions reveals clusters.

- Common intermediaries
- Same on-chain behavior
- Metadata correlation

### Implementation

Source: `src/detection/sybil.py`

---

## Layering Detection

Identifies multi-hop money laundering.

### Patterns

#### 1. Fan-out Pattern

```
One wallet → Many wallets
```

#### 2. Circular Pattern

```
A → B → C → A
```

#### 3. Multi-hop Pattern

```
A → B → C → D → E (destination)
```

### Implementation

Source: `src/detection/layering.py`

---

## Risk Scoring Weights

| Flag | Weight |
|------|-------|
| mixer_direct | 40 |
| mixer_indirect | 25 |
| bridge_direct | 15 |
| chain_hopping | 10 |
| sybil_cluster | 25 |
| layering_fan_pattern | 20 |
| layering_circular | 25 |
| layering_multi_hop | 15 |

### Score Calculation

```
total_score = min(mixer_score + bridge_score + sybil_score + layering_score, 100)
```

Where each score = weight * (confidence / 100)

---

## Data Sources

| Source | Data |
|--------|------|
| Polymarket API | Trades, positions, users |
| Polygon RPC | On-chain transfers |
| Dune | Historical analysis |
| Goldsky | Subgraph data |

---

## See Also

- [Risk Scoring](risk-scoring.md)
- [Network Analysis](network-analysis.md)
- [Source Code](../../src/detection/)