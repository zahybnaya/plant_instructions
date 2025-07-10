#!/usr/bin/env python3
import os
import sys
import argparse
import re
import requests
import subprocess
import json
from groq import Groq



# Path to the state file that tracks if tinyllama model is available
#MODEL_STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".tinyllama_available")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def sanitize_filename(name):
    """Convert plant name to a safe filename."""
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name.lower())
   

#checking if the API running, pls debug
def check_groq():
    if not GROQ_API_KEY: 
        return False, "no Groq for u my dear"
    return True, "Api available"
    
#do not touch
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
 #here u started changing the code to use groq
   
    try:
        # Check if api key is available
        key_available, status_message = check_groq()
        
        if not key_available:
            print(f"Error: {status_message}")
            return None
        
            
        # Generate text using Groq API - again???
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

            #API KEY:
            #python groq_1.py

            # 200 OK: The request was successfully executed. No further action is needed.

                
                # Check if the plant is unknown
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

#file path - do not touch
def save_instructions(plant_name, instructions):
    """Save the generated instructions to a markdown file."""
    # Create instructions directory if it doesn't exist
    os.makedirs("plant_instructions", exist_ok=True)
    
    if instructions is None:
        # Store None if plant is unknown
        result_file = os.path.join("plant_instructions", f"{sanitize_filename(plant_name)}.txt")
        with open(result_file, "w") as f:
            f.write("None")
        print(f"Plant '{plant_name}' is unknown. Stored 'None' in {result_file}")
        return None
    else:
        # Save markdown file
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
        
    # Generate and save instructions
    instructions = generate_instructions(args.plant_name)
    save_instructions(args.plant_name, instructions)

if __name__ == "__main__":
    main() 


    #https://console.groq.com/docs/errors - documentry for error Groq 

    