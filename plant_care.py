#!/usr/bin/env python3
import os
import sys
import argparse
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def check_groq():
    """Check if Groq API key is available."""
    if not GROQ_API_KEY: 
        return False, "No Groq API key found. Please set GROQ_API_KEY environment variable."
    return True, "API available"

def generate_instructions(plant_name):
    """Generate care instructions for the given plant using Groq API."""
    prompt = f"""
    Create comprehensive care instructions for the plant known as '{plant_name}'.
    
    Please include:
    - Common and scientific name(s)
    - Watering requirements (frequency, amount)
    - Light needs (direct sun, partial shade, etc.)
    - Soil preferences 
    - Temperature and humidity requirements
    - Fertilization schedule
    - Propagation methods
    - Common problems and solutions
    - Any special care notes
    
    Format the response as a markdown document with appropriate sections and headings.
    If this is not a known plant, please indicate that clearly.
    """

    try:
        key_available, status_message = check_groq()
        
        if not key_available:
            print(f"Error: {status_message}")
            return None
        
        client = Groq(api_key=GROQ_API_KEY)

        chat_completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_completion_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )

        return chat_completion.choices[0].message.content

    except Exception as e:
        print(f"Error generating instructions: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(
        description="Generate plant care instructions using AI"
    )
    parser.add_argument(
        "plant_name", help="Name of the plant to generate care instructions for"
    )

    args = parser.parse_args()

    if not args.plant_name:
        print("Error: Plant name is required")
        sys.exit(1)

    # Generate instructions
    instructions = generate_instructions(args.plant_name)
    
    # Output the instructions directly to console
    if instructions is None:
        print(f"Plant '{args.plant_name}' is unknown.")
    else:
        print(f"# {args.plant_name} Care Instructions\n")
        print(instructions)

if __name__ == "__main__":
    main()

