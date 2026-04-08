# Risk Scoring

Aggregate risk scores for wallets (0-100 scale).

## Overview

Risk scoring combines all detection flags into a single metric.

```
Risk Score = min(mixer + bridge + sybil + layering, 100)
```

## Score Ranges

| Score | Risk Level | Action |
|-------|-----------|--------|
| 0-24 | Low | Normal |
| 25-49 | Medium | Monitor |
| 50-74 | High | Flag |
| 75-100 | Critical | Prioritize |

## Weight Definitions

| Flag Type | Weight | Max Contribution |
|----------|--------|---------------|
| mixer_direct | 40 | 40 |
| mixer_indirect | 25 | 25 |
| bridge_direct | 15 | 15 |
| chain_hopping | 10 | 10 |
| sybil_cluster | 25 | 25 |
| layering_fan_pattern | 20 | 20 |
| layering_circular | 25 | 25 |
| layering_multi_hop | 15 | 15 |

## Calculation

### Per-Wallet

```python
def calculate_score(flags):
    mixer_score = 0
    bridge_score = 0
    sybil_score = 0
    layering_score = 0
    
    for flag in flags:
        weight = RISK_WEIGHTS[flag.type]
        contribution = weight * (flag.confidence / 100)
        
        if flag.type.startswith("mixer"):
            mixer_score = max(mixer_score, contribution)
        elif flag.type.startswith("bridge") or flag.type.startswith("chain"):
            bridge_score = max(bridge_score, contribution)
        elif flag.type.startswith("sybil"):
            sybil_score = max(sybil_score, contribution)
        elif flag.type.startswith("layering"):
            layering_score = max(layering_score, contribution)
    
    total = min(mixer_score + bridge_score + sybil_score + layering_score, 100)
    return total
```

### Key Points

- Use MAX for category (not sum)
- Multiple flags in same category don't stack
- Cap at 100

## Distribution

```python
distribution = {
    "low_risk": count where score < 25,
    "medium_risk": 25 <= score < 50,
    "high_risk": 50 <= score < 75,
    "critical_risk": score >= 75
}
```

## Usage in This Project

1. Run detection on wallets
2. Calculate scores
3. Flag wallets above threshold
4. Generate report

```python
# Flagged wallets (score >= 25)
flagged = scorer.get_flagged_wallets(min_score=25)
```

## Example

Wallet has:
- mixer_direct @ 95% confidence = 40 * 0.95 = 38
- sybil_cluster @ 60% confidence = 25 * 0.60 = 15

Total = 38 + 15 = 53 (High risk)

## Implementation

Source: `src/analysis/risk_scorer.py`

## See Also

- [Detection Methods](detection-methods.md)
- [Source Code](../../src/analysis/risk_scorer.py)