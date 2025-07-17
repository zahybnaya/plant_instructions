#!/bin/bash

if [[ "$OSTYPE" == "msys"  "$OSTYPE" == "cygwin"  "$OSTYPE" == "win32" ]]; then
    OS="windows"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="mac"
else
    OS="linux"
fi


echo "Creating virtual environment..."
if [[ "$OS" == "windows" ]]; then
    python -m venv venv
else
    python3 -m venv venv
fi


echo "Activating virtual environment..."
if [[ "$OS" == "windows" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi


echo "Installing required packages..."
pip install -r requirements.txt


if [[ "$OS" != "windows" ]]; then
    chmod +x plant_care.py
fi

echo ""
echo "Setup complete!"
echo ""


if [[ "$OS" == "windows" ]]; then
    echo "To run the tool:"
    echo "1. Activate virtual environment: venv\\Scripts\\activate"
    echo "2. Run: python plant_care.py \"Plant Name\""
    echo ""
    echo "Or run directly with:"
    echo "venv\\Scripts\\python plant_care.py \"Plant Name\""
else
    echo "To run the tool:"
    echo "1. Activate virtual environment: source venv/bin/activate"
    echo "2. Run: python plant_care.py \"Plant Name\""
    echo ""
    echo "Or run directly with:"
    echo "./venv/bin/python plant_care.py \"Plant Name\""
    echo ""
    echo "If you made the script executable, you can also run:"
    echo "./plant_care.py \"Plant Name\""
fi