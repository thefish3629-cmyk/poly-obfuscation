#!/bin/bash
# Polymarket Obfuscation Detection Pipeline Setup Script

echo "========================================"
echo "Polymarket Obfuscation Detector Setup"
echo "========================================"

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "ERROR: Python is not installed or not in PATH"
    exit 1
fi

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed or not in PATH"
    exit 1
fi

echo ""
echo "Step 1: Starting Docker containers..."
docker compose up -d

echo ""
echo "Step 2: Waiting for databases to be ready..."
sleep 10

echo ""
echo "Step 3: Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "Step 4: Creating .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file - please edit it with your API keys"
else
    echo ".env already exists, skipping..."
fi

echo ""
echo "========================================"
echo "Setup complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys:"
echo "   - POLYGON_RPC_URL (get free key at alchemy.com)"
echo "   - DUNE_API_KEY (get at dune.com)"
echo "2. Run: python -m src.main"
echo ""
