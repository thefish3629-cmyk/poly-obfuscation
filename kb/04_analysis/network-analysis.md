# Network Analysis

Graph-based analysis of wallet relationships.

## Graph Structure

Vertices: Wallets, contracts
Edges: Transfers, interactions

```
Wallet A → Wallet B (transferred USDC)
```

## Tools

| Tool | Use |
|------|-----|
| NetworkX | Graph operations |
| Neo4j | Graph database |
| Graphviz | Visualization |

## Graph Types

### Transfer Graph

```
(wallet) --[transfers]--> (wallet)
```

### Funding Graph

```
(source) --[funds]--> (destination)
```

### Contract Interaction Graph

```
(wallet) --[calls]--> (contract)
```

## Key Metrics

### Centrality

Identify influential wallets.

| Metric | Meaning |
|--------|---------|
| Degree | Number of connections |
| Betweenness | Bridge between clusters |
| PageRank | Overall importance |

### Clustering

Find wallet clusters.

- Community detection
- Connected components
- Dense subgraphs

## Analysis Techniques

### 1. Path Finding

Trace fund origin.

```python
import networkx as nx

G = nx.DiGraph()
# Add edges...

# Shortest path
path = nx.shortest_path(G, source, target)
```

### 2. Community Detection

Find related wallets.

```python
from networkx.algorithms import community

clusters = list(community.greedy_modularity_communities(G))
```

### 3. Cycle Detection

Find circular patterns.

```python
cycles = list(nx.simple_cycles(G))
# layering_circular detection
```

## Visualization

### NetworkX + Matplotlib

```python
import matplotlib.pyplot as plt
import networkx as nx

pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True)
plt.show()
```

### Neo4j + Browser

```graphQL
MATCH (w:Wallet)
RETURN w
```

## Common Patterns

### Fan-out

```
A → B, C, D, E
```

Detects: Layering (fan-out pattern)

### Chain

```
A → B → C → D
```

Detects: Money laundering chain

### Cycle

```
A → B → C → A
```

Detects: Circular layering

## Implementation

### Build Graph from Trades

```python
for trade in trades:
    G.add_edge(
        trade["user"],
        trade["market"],
        trade={"amount": trade["amount"]}
    )
```

### Query Neo4j

```python
from py2neo import Graph

graph = Graph("bolt://localhost:7687", password="password")
result = graph.run("MATCH (w:Wallet)-[:TRANSFERRED]->(to) RETURN w, to")
```

## Use Cases

1. **Sybil Detection**: Find clusters
2. **Layering Detection**: Find patterns
3. **Bridge Detection**: Track cross-chain
4. **Risk Scoring**: Network features

## See Also

- [Detection Methods](detection-methods.md)
- [Risk Scoring](risk-scoring.md)
- [Source Code](../../src/storage/graph_store.py)