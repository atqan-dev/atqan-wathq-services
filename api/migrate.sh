#!/bin/bash
# Simple wrapper script for running migrations
# Usage: ./migrate.sh [options]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}==================================================================${NC}"
echo -e "${GREEN}Database Migration Script${NC}"
echo -e "${GREEN}==================================================================${NC}"

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo -e "${RED}Error: 'uv' command not found${NC}"
    echo "Please install uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Run the migration script with all arguments passed through
echo -e "${YELLOW}Running migrations...${NC}"
uv run python scripts/run_migrations.py "$@"

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}==================================================================${NC}"
    echo -e "${GREEN}Migration completed successfully!${NC}"
    echo -e "${GREEN}==================================================================${NC}"
else
    echo -e "${RED}==================================================================${NC}"
    echo -e "${RED}Migration failed with exit code: $exit_code${NC}"
    echo -e "${RED}==================================================================${NC}"
fi

exit $exit_code
