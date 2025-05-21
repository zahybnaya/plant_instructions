#!/bin/bash

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required packages
pip install -r requirements.txt

# Make the script executable
chmod +x plant_care.py

echo "Setup complete! You can now run the tool with:"
echo "./venv/bin/python plant_care.py \"Plant Name\""
echo "Or activate the virtual environment first with:"
echo "source venv/bin/activate"
echo "Then run:"
echo "./plant_care.py \"Plant Name\"" 