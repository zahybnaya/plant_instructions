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
    
=======

# Path to the state file that tracks if tinyllama model is available
MODEL_STATE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".tinyllama_available"
)


def sanitize_filename(name):
    """Convert plant name to a safe filename."""
    return re.sub(r"[^a-zA-Z0-9_-]", "_", name.lower())


def check_ollama_status():
    """Check if Ollama is running and if the tinyllama model is available."""
    # If we've previously confirmed model availability, skip the check
    if os.path.exists(MODEL_STATE_FILE):
        return True, "Model available (cached)"

    try:
        # Check if Ollama server is running
        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code != 200:
                return False, "Ollama server not responding correctly"
        except requests.exceptions.ConnectionError:
            return (
                False,
                "Ollama server is not running. Please start it with 'ollama serve'",
            )

        # Check if tinyllama model is available
        models = response.json().get("models", [])
        model_names = [model["name"] for model in models]

        if "tinyllama" in model_names:
            # Model is available, create the state file to remember this
            with open(MODEL_STATE_FILE, "w") as f:
                f.write("Model is available")
            return True, "Model available"
        else:
            # Also check if the model is being pulled or in progress
            try:
                # Check local model list (which includes models being downloaded)
                response = requests.get("http://localhost:11434/api/local")
                if response.status_code == 200:
                    local_models = response.json().get("models", [])
                    if any(model["name"] == "tinyllama" for model in local_models):
                        return False, "Model download in progress or incomplete"
            except:
                pass

            return False, "Model not available"

    except Exception as e:
        return False, f"Error checking Ollama status: {str(e)}"



def call_ollama_api(model, prompt):
    """Make a request to the Ollama API and return the response text."""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
        )

        if response.status_code == 200:
            result = response.json()
            return result.get("response", "")
        else:
            # If API call fails, it might be because model wasn't actually ready
            # Remove the state file so we'll check again next time
            if os.path.exists(MODEL_STATE_FILE):
                os.remove(MODEL_STATE_FILE)
            print(
                f"Error: API request failed with status code {response.status_code}"
            )
            return None
    except requests.exceptions.ConnectionError:
        # If connection fails, remove state file to force a recheck next time
        if os.path.exists(MODEL_STATE_FILE):
            os.remove(MODEL_STATE_FILE)
        print("Error: Lost connection to Ollama server")
        return None


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
                  


=======

    try:
        # Check if Ollama is running and model is available
        model_available, status_message = check_ollama_status()

        if not model_available:
            if "not running" in status_message:
                print(f"Error: {status_message}")
                return None
            elif "Model not available" in status_message:
                print("tinyllama model not found. You need to pull it first.")
                user_input = 'y'
                if user_input.lower() == 'y':
                    print("Pulling tinyllama model (this may take a while)...")
                    try:
                        subprocess.run(["ollama", "pull", "tinyllama"], check=True)
                        print("Model downloaded successfully!")
                        # Create the state file to remember the model is available
                        with open(MODEL_STATE_FILE, "w") as f:
                            f.write("Model is available")
                    except subprocess.CalledProcessError:
                        print(
                            "Failed to download the model. Please try manually with 'ollama pull tinyllama'"
                        )
                        return None
                else:
                    print(
                        "Please run 'ollama pull tinyllama' manually before using this tool."
                    )
                    return None
            else:
                print(f"Error: {status_message}")
                return None

        # Generate text using Ollama API
        generated_text = call_ollama_api("tinyllama", prompt)
        
        if generated_text is None:
            return None

        # Check if the plant is unknown
        unknown_patterns = [
            "not a known plant",
            "don't recognize this plant",
            "couldn't find information",
            "not a recognized plant",
            "unable to identify",
            "not a valid plant",
        ]

        if any(
            pattern.lower() in generated_text.lower()
            for pattern in unknown_patterns
        ):
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
=======
    """Print the generated instructions as markdown to the console."""
    if instructions is None:
        print(f"Plant '{plant_name}' is unknown.")
        return None
    else:
        # Print markdown content to console
        print(f"# {plant_name} Care Instructions\n")
        print(instructions)
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

        

=======

    # Generate and save instructions

    instructions = generate_instructions(args.plant_name)
    save_instructions(args.plant_name, instructions)


if __name__ == "__main__":

    main() 


    
=======
    main()

