# Plant Care Instructions Generator

A command-line tool that generates care instructions for plants using Ollama's tinyllama model.

## Requirements

- Python 3
- [Ollama](https://ollama.ai/) installed and running with the tinyllama model

## Setup

1. Clone this repository
2. Run the setup script to create a virtual environment and install dependencies:

```bash
chmod +x setup.sh
./setup.sh
```

3. Install the tinyllama model for Ollama (if not already installed):

```bash
# Start Ollama server if not running
ollama serve  # Run this in a separate terminal or add & to run in background

# Pull the tinyllama model
ollama pull tinyllama
```

## Usage

1. Make sure Ollama is running:
```bash
ollama serve
```

2. Run the tool with a plant name:
```bash
# Using the virtual environment python
./venv/bin/python plant_care.py "Monstera Deliciosa"

# OR activate the virtual environment first
source venv/bin/activate
./plant_care.py "Snake Plant"
```

3. The generated care instructions will be saved as a markdown file in the `plant_instructions` directory.

4. If the plant is unknown, a file containing "None" will be created instead.

## Example

```bash
./plant_care.py "Fiddle Leaf Fig"
```

This will generate a markdown file with comprehensive care instructions for a Fiddle Leaf Fig plant. 
