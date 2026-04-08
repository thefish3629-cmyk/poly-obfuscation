# Polymarket Obfuscation Detection Pipeline

A data analysis pipeline for detecting traders on Polymarket who are obfuscating the origin of their trades through mixers, bridges, and wallet clustering.

## Target Market
**"Israel strike on Iranian nuclear facility before July?"**

## Features

- **Mixer Detection**: Identify trades funded via Tornado Cash, Railgun, Aztec
- **Bridge Detection**: Track cross-chain fund flows through major bridges
- **Sybil Detection**: Cluster wallets controlled by the same entity
- **Layering Detection**: Identify multi-hop fund paths and money laundering patterns
- **Risk Scoring**: Aggregate risk scores for each wallet (0-100 scale)

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA INGESTION LAYER                          │
├──────────────┬──────────────┬──────────────┬────────────────────────┤
│ Polymarket   │ Goldsky      │ Dune         │ Polygon RPC            │
│ APIs         │ Subgraphs    │ Analytics    │ (web3.py)              │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           STORAGE LAYER                              │
├─────────────────────────────────┬───────────────────────────────────┤
│ PostgreSQL                      │ Neo4j (Graph DB)                  │
└─────────────────────────────────┴───────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      DETECTION MODULES                               │
├─────────────────┬─────────────────┬─────────────────────────────────┤
│ Mixer Detection │ Bridge Detection│ Sybil Detection                 │
├─────────────────┴─────────────────┴─────────────────────────────────┤
│ Layering Detection                                                   │
└─────────────────────────────────────────────────────────────────────┘
```

## Setup

### 1. Start Infrastructure

```bash
docker compose up -d
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Create `.env` file:
```
POLYGON_RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY
DUNE_API_KEY=YOUR_DUNE_KEY
GOLDSKY_API_KEY=YOUR_GOLDSKY_KEY
```

### 4. Run the Pipeline

```bash
python -m src.data.ingest --market "israel-strike-iran-nuclear-facility-before-july"
python -m src.detection.run_all
python -m src.analysis.report
```

## Project Structure

```
polymarket-obfuscation-detector/
├── src/
│   ├── data/           # API clients
│   ├── models/         # Database schemas
│   ├── storage/        # PostgreSQL & Neo4j operations
│   ├── detection/      # Detection modules
│   ├── analysis/       # Risk scoring & reporting
│   └── utils/          # Config & utilities
├── tests/              # Unit tests with pytest
├── notebooks/          # Jupyter notebooks for analysis
├── data/               # Local data storage
├── reports/            # Generated reports
├── logs/               # Application logs
└── docker-compose.yml  # Database infrastructure
```

## Testing

Run all tests:
```bash
pytest
```

Run specific test file:
```bash
pytest tests/test_mixers.py -v
```

Run with coverage:
```bash
pytest --cov=src --cov-report=html
```

## Notebooks

1. **01_data_exploration.ipynb** - Explore trade data and wallet statistics
2. **02_fund_flow_analysis.ipynb** - Trace fund origins and analyze flows
3. **03_risk_dashboard.ipynb** - Visualize risk scores and distributions
4. **04_network_visualization.ipynb** - Graph analysis with NetworkX

Start Jupyter:
```bash
jupyter notebook notebooks/
```

## Dashboard

Run the Streamlit dashboard:
```bash
streamlit run dashboard.py
```

## Risk Scoring

| Flag | Weight |
|------|--------|
| Tornado/Mixer interaction | 40 |
| Sybil cluster membership | 25 |
| Layering detected | 20 |
| Cross-chain bridge usage | 15 |
| High volume anomaly | 10 |
| Timing anomaly | 5 |

## License

MIT
