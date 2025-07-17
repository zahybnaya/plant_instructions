#!/usr/bin/env python3
import os
import sys
import argparse
import re
import requests
import subprocess
import json
from groq import Groq




GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def sanitize_filename(name):
    """Convert plant name to a safe filename."""
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name.lower())
   


def check_groq():
    if not GROQ_API_KEY: 
        return False, "no Groq for u my dear"
    return True, "Api available"
    

def generate_instructions(plant_name):
    """Generate care instructions for the given plant using Groq api."""
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
        
            
        
        client=Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )


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

        generated_text = chat_completion.choices[0].message.content

        unknown_patterns = [
                    "not a known plant",
                    "don't recognize this plant",
                    "couldn't find information",
                    "not a recognized plant",
                    "unable to identify",
                    "not a valid plant"
                ]
                
        if any(pattern.lower() in generated_text.lower() for pattern in unknown_patterns):
            print(f"'{plant_name}' appears to be unknown.")
            return None
                    
        return generated_text
                  


    except Exception as e:
        print(f"Error generating instructions: {str(e)}")
        return None


def save_instructions(plant_name, instructions):
    """Save the generated instructions to a markdown file."""
    
    os.makedirs("plant_instructions", exist_ok=True)
    
    if instructions is None:
       
        result_file = os.path.join("plant_instructions", f"{sanitize_filename(plant_name)}.txt")
        with open(result_file, "w") as f:
            f.write("None")
        print(f"Plant '{plant_name}' is unknown. Stored 'None' in {result_file}")
        return None
    else:
        
        filename = f"{sanitize_filename(plant_name)}.md"
        filepath = os.path.join("plant_instructions", filename)
        
        with open(filepath, "w") as f:
            f.write(f"# {plant_name} Care Instructions\n\n")
            f.write(instructions)
            
        print(f"Care instructions for '{plant_name}' saved to {filepath}")
        return filepath

def main():
    parser = argparse.ArgumentParser(description="Generate plant care instructions using AI")
    parser.add_argument("plant_name", help="Name of the plant to generate care instructions for")
    
    args = parser.parse_args()
    
    if not args.plant_name:
        print("Error: Plant name is required")
        sys.exit(1)
        
    
    instructions = generate_instructions(args.plant_name)
    save_instructions(args.plant_name, instructions)

if __name__ == "__main__":
    main() 


    

    