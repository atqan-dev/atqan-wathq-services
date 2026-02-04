#!/bin/bash
# =============================================================================
# Atqan WATHQ Services - Database Refresh Script
# =============================================================================
# This script:
# 1. Drops all tables and recreates the database schema
# 2. Runs all migrations
# 3. Seeds the database with initial data
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}"
echo "=============================================================="
echo "  ATQAN WATHQ SERVICES - DATABASE REFRESH"
echo "=============================================================="
echo -e "${NC}"

# Change to API directory
cd "$API_DIR"

# Check if virtual environment exists
if [ -d ".venv" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source .venv/bin/activate
else
    echo -e "${RED}Virtual environment not found at $API_DIR/.venv${NC}"
    echo "Please create it first: python -m venv .venv && pip install -r requirements.txt"
    exit 1
fi

# Confirm action
echo -e "${YELLOW}"
echo "WARNING: This will DROP ALL TABLES and recreate the database!"
echo -e "${NC}"
read -p "Are you sure you want to continue? (y/N): " confirm

if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo -e "${RED}Aborted.${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}Step 1: Dropping all tables...${NC}"
python -c "
from app.db.session import engine
from app.db.base import Base
Base.metadata.drop_all(bind=engine)
print('All tables dropped.')
"

echo ""
echo -e "${BLUE}Step 2: Running Alembic migrations...${NC}"
alembic upgrade head

echo ""
echo -e "${BLUE}Step 3: Seeding database...${NC}"
python scripts/seed_all_data.py

echo ""
echo -e "${GREEN}"
echo "=============================================================="
echo "  DATABASE REFRESH COMPLETED SUCCESSFULLY!"
echo "=============================================================="
echo -e "${NC}"
echo "You can now restart the API service:"
echo "  sudo systemctl restart atqan-api"
echo ""
