# Plant Care Instructions Generator

A command-line tool that generates care instructions for plants using Groq's AI API.

## Requirements

- Python 3
- Groq API key

## Setup

1. Clone this repository
2. Run the setup script to create a virtual environment and install dependencies:

```bash
chmod +x setup.sh
./setup.sh
```

3. Set your Groq API key as an environment variable:

```bash
export GROQ_API_KEY="your_groq_api_key_here"
```

You can get a free API key from [Groq](https://console.groq.com/).

## Usage

1. Make sure your Groq API key is set:
```bash
export GROQ_API_KEY="your_groq_api_key_here"
```

2. Run the tool with a plant name:
```bash
# Using the virtual environment python
./venv/bin/python plant_care.py "Monstera Deliciosa"

# OR activate the virtual environment first
source venv/bin/activate
python plant_care.py "Snake Plant"
```

3. The generated care instructions will be displayed directly in the console as markdown.

## Example

```bash
python plant_care.py "Fiddle Leaf Fig"
```

This will generate and display comprehensive care instructions for a Fiddle Leaf Fig plant directly in the terminal.

## Features

- Generates comprehensive plant care instructions including:
  - Common and scientific names
  - Watering requirements
  - Light needs
  - Soil preferences
  - Temperature and humidity requirements
  - Fertilization schedule
  - Propagation methods
  - Common problems and solutions
  - Special care notes
- Uses Groq's fast AI model for quick responses
- Outputs formatted markdown directly to console 
