#!/usr/bin/env bash
set -e

echo "Setting up Python environment and dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Setup completed successfully."
