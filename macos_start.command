#!/bin/bash

cd "$(dirname "$0")"
echo "🚀 Starting project"

exec uv run python main.py
