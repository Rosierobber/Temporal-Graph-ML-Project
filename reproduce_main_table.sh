#!/usr/bin/env bash
set -e
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"
python3 scripts/reproduce_table.py 2>/dev/null || python scripts/reproduce_table.py
