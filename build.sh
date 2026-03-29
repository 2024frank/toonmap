#!/usr/bin/env bash
set -o errexit

echo "Installing Python dependencies with pre-built wheels..."
pip install --upgrade pip
pip install --only-binary=:all: fastapi uvicorn requests python-dotenv openai Pillow huggingface-hub 2>/dev/null || pip install -r requirements.txt
