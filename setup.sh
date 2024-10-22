#!/bin/bash

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install dependencies
pip install -r requirements.txt

# Initialize database
python setup_database.py

echo "Setup complete."
