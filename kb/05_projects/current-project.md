# Polymarket Obfuscation Detector

Analysis pipeline for detecting traders obfuscating fund origins.

## Purpose

Detect traders on Polymarket using mixers, bridges, and wallet clustering to hide trade origins.

## GitHub

```
https://github.com/thefish3629-cmyk/poly-obfuscation
```

## Features

- **Mixer Detection**: Tornado Cash, Railgun, Aztec
- **Bridge Detection**: Cross-chain tracking
- **Sybil Detection**: Wallet clustering
- **Layering Detection**: Multi-hop patterns
- **Risk Scoring**: 0-100 scale

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python |
| APIs | Polymarket, Dune, Goldsky, Polygon |
| Storage | PostgreSQL, Neo4j |
| Dashboard | Streamlit |
| Notebooks | Jupyter |

## Setup

```bash
# Clone
git clone https://github.com/thefish3629-cmyk/poly-obfuscation.git
cd poly-obfuscation

# Install
pip install -r requirements.txt

# Configure
cp .env.example .env
# Add API keys:
# - POLYGON_RPC_URL (Alchemy)
# - DUNE_API_KEY
# - GOLDSKY_API_KEY

# Start databases
docker compose up -d

# Run
python -m src.main
```

## Run Commands

```bash
# Full pipeline
python -m src.main

# Just detection
python -m src.detection.run_all

# Generate report
python -m src.analysis.reporter

# Dashboard
streamlit run dashboard.py

# Jupyter
jupyter notebook notebooks/
```

## Architecture

```
┌─────────────────────────────────┐
│      Data Ingestion              │
│  Polymarket, Dune, Goldsky       │
└───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│      Storage                   │
│  PostgreSQL, Neo4j            │
└───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│      Detection                 │
│  Mixers, Bridges, Sybil       │
│  Layering                  │
└───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│      Analysis                 │
│  Risk Scoring, Reporting     │
└───────────────────────────────┘
```

## Current Target

**Market**: "Will Israel strike Iranian nuclear facility before July?"

## Reports

Generated in `/reports/`:
- `flagged_wallets_*.csv` - Wallet list with flags
- `report_*.json` - Full analysis report

## Status

- Status: Active
- Last run: 2026-04-08

## Knowledge Base

This project's knowledge base is in `/kb/`:
- API docs: [kb/02_apis/](kb/02_apis/)
- Detection: [kb/04_analysis/](kb/04_analysis/)
- Polymarket: [kb/03_polymarket/](kb/03_polymarket/)

## See Also

- [Knowledge Base](kb/_index.md)
- [README](../../README.md)