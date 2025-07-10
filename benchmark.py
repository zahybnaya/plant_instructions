#!/usr/bin/env python3
import os
import subprocess
import time
import json
import requests
import re
import datetime


PLANTS_FILE = "plants.txt"
INSTRUCTIONS_DIR = "plant_instructions"
RESULTS_FILE = "benchmark_results_{}.md"  # Will be formatted with timestamp
PHI3_MODEL_NAME = "phi3:mini" # Using phi3:mini model for evaluation

# Global variable to track if we've checked for the model
CHECKED_MODEL = False
MODEL_TO_USE = PHI3_MODEL_NAME

def get_timestamp():
    """Get current timestamp in a readable format."""
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def run_plant_care(plant_name):
    """Run the plant_care.py script for a given plant name."""
    print(f"Generating instructions for: {plant_name}")
    try:
        # Run the plant_care.py script
        result = subprocess.run(
            ["./plant_care.py", plant_name],
            capture_output=True,
            text=True,
            check=False
        )
        
        # Check if the command was successful
        if result.returncode != 0:
            print(f"Error generating instructions for {plant_name}:")
            print(result.stderr)
            return False
            
        print(f"Successfully generated instructions for {plant_name}")
        return True
    except Exception as e:
        print(f"Exception when generating instructions for {plant_name}: {str(e)}")
        return False

def get_instruction_path(plant_name):
    """Get the path to the instruction file for a given plant."""
    # Convert plant name to filename format
    sanitized_name = re.sub(r'[^a-zA-Z0-9_-]', '_', plant_name.lower())
    
    # Check for markdown file
    md_path = os.path.join(INSTRUCTIONS_DIR, f"{sanitized_name}.md")
    if os.path.exists(md_path):
        return md_path
        
    # Check for text file (indicating None)
    txt_path = os.path.join(INSTRUCTIONS_DIR, f"{sanitized_name}.txt")
    if os.path.exists(txt_path):
        return txt_path
        
    return None

def instructions_exist(plant_name):
    """Check if instructions for this plant already exist."""
    return get_instruction_path(plant_name) is not None

def read_instruction_file(file_path):
    """Read the content of an instruction file."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return None

def check_model_availability():
    """Check if the evaluation model is available and cache the result."""
    global CHECKED_MODEL
    
    # If we've already checked, use the cached result
    if CHECKED_MODEL:
        return PHI3_MODEL_NAME
    
    try:
        # Check if phi3:mini model is available
        print(f"Checking if {PHI3_MODEL_NAME} is available...")
        response = requests.get("http://localhost:11434/api/tags")
        models = response.json().get("models", [])
        model_names = [model["name"] for model in models]
        
        # Print available models for debugging
        print(f"Available models: {', '.join(model_names)}")
        
        phi3_available = PHI3_MODEL_NAME in model_names
        
        if not phi3_available:
            print(f"{PHI3_MODEL_NAME} not found. Attempting to pull it...")
            try:
                # Pull the phi3:mini model
                print(f"Running: ollama pull {PHI3_MODEL_NAME}")
                subprocess.run(["ollama", "pull", PHI3_MODEL_NAME], check=True)
                print(f"Successfully pulled {PHI3_MODEL_NAME} model")
            except subprocess.CalledProcessError as e:
                print(f"Error pulling {PHI3_MODEL_NAME} model: {str(e)}")
                print(f"Cannot proceed without {PHI3_MODEL_NAME} model. Benchmark will fail.")
                # Still return the model name, but evaluation will fail
        else:
            print(f"{PHI3_MODEL_NAME} is available and will be used for evaluation")
        
        # Mark that we've checked for the model
        CHECKED_MODEL = True
        return PHI3_MODEL_NAME
        
    except Exception as e:
        print(f"Error checking model availability: {str(e)}")
        CHECKED_MODEL = True  # Mark as checked to avoid repeated errors
        return PHI3_MODEL_NAME

def evaluate_with_phi3(plant_name, instructions):
    """Evaluate the plant care instructions using phi3:mini model."""
    # Get the model to use (checks only once per benchmark run)
    check_model_availability()  # Just check availability
    model_to_use = PHI3_MODEL_NAME  # Always use phi3:mini
    
    # Check if it's a "None" file
    if os.path.splitext(instructions)[1] == '.txt':
        with open(instructions, 'r') as f:
            content = f.read().strip()
            if content == "None":
                # For "None" files (unknown plants)
                prompt = f"""
                You are a strict evaluator of plant care instructions.

                Your job is to judge whether the response provided for a given plant name is:
                - Factually correct
                - Clear and actionable
                - Appropriate for the plant

                You must return only one of two verdicts: PASS or FAIL.

                ---

                Input:
                {plant_name}

                Response:
                "The plant is unknown or doesn't exist."

                ---

                Evaluate the response. If this plant truly doesn't exist or is extremely rare, respond with PASS. 
                If this is a common plant that should have care instructions, respond with FAIL.

                Only respond with PASS or FAIL, followed by a one-sentence reason.
                """
            else:
                return "ERROR", "Unexpected content in text file"
    else:
        # For instruction files, evaluate the quality
        instruction_content = read_instruction_file(instructions)
        if instruction_content is None:
            return "ERROR", "Could not read instruction file"
            
        prompt = f"""
        You are a strict evaluator of plant care instructions.

        Your job is to judge whether the response provided for a given plant name is:
        - Factually correct
        - Clear and actionable
        - Appropriate for the plant

        You must return only one of two verdicts: PASS or FAIL.

        ---

        Input:
        {plant_name}

        Response:
        {instruction_content[:3500]}

        ---

        Evaluate the response. If the instructions are correct and useful for caring for this plant, respond with PASS. Otherwise, respond with FAIL.

        Only respond with PASS or FAIL, followed by a one-sentence reason.
        """
    
    try:
        # Use model to evaluate the instructions
        print(f"Evaluating with {model_to_use} model...")
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_to_use,
                "prompt": prompt,
                "stream": False
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            evaluation = result.get("response", "").strip()
            
            # Extract the PASS/FAIL result
            if evaluation.upper().startswith("PASS"):
                return "PASS", evaluation
            elif evaluation.upper().startswith("FAIL"):
                return "FAIL", evaluation
            else:
                # Try more general pattern
                if "PASS" in evaluation[:50]:
                    return "PASS", evaluation
                elif "FAIL" in evaluation[:50]:
                    return "FAIL", evaluation
                else:
                    return "UNCLEAR", evaluation
        else:
            return "ERROR", f"API request failed with status code {response.status_code}"
    except Exception as e:
        return "ERROR", f"Error evaluating instructions: {str(e)}"

def generate_all_instructions(plants):
    """Phase 1: Generate instructions for all plants."""
    print("\n" + "="*50)
    print("PHASE 1: GENERATING INSTRUCTIONS")
    print("="*50)
    
    generation_results = []
    
    for plant in plants:
        print(f"\nProcessing plant: {plant}")
        
        # Skip if instructions already exist
        if instructions_exist(plant):
            print(f"Instructions for '{plant}' already exist, skipping generation")
            generation_results.append({
                "plant": plant,
                "status": "SKIPPED",
                "reason": "Instructions already exist"
            })
            continue
        
        # Run plant_care.py to generate instructions
        success = run_plant_care(plant)
        
        if success:
            generation_results.append({
                "plant": plant,
                "status": "SUCCESS"
            })
        else:
            generation_results.append({
                "plant": plant,
                "status": "FAILED",
                "reason": "Error generating instructions"
            })
    
    # Print generation summary
    success_count = len([r for r in generation_results if r["status"] == "SUCCESS"])
    skipped_count = len([r for r in generation_results if r["status"] == "SKIPPED"])
    failed_count = len([r for r in generation_results if r["status"] == "FAILED"])
    
    print("\nGeneration Summary:")
    print(f"Generated: {success_count}")
    print(f"Skipped: {skipped_count}")
    print(f"Failed: {failed_count}")
    
    return generation_results

def evaluate_all_instructions(plants):
    """Phase 2: Evaluate all generated instructions."""
    print("\n" + "="*50)
    print("PHASE 2: EVALUATING INSTRUCTIONS")
    print("="*50)
    
    # Check model availability once before starting evaluations
    check_model_availability()
    print(f"Using model {PHI3_MODEL_NAME} for all evaluations")
    
    evaluation_results = []
    
    for plant in plants:
        print(f"\nEvaluating: {plant}")
        
        # Get path to instruction file
        instruction_path = get_instruction_path(plant)
        
        if not instruction_path:
            print(f"No instructions found for '{plant}', skipping evaluation")
            evaluation_results.append({
                "plant": plant,
                "status": "ERROR",
                "reason": "No instructions found",
                "result": "FAIL"
            })
            continue
        
        # Evaluate with phi3:mini
        result, explanation = evaluate_with_phi3(plant, instruction_path)
        print(f"Evaluation result: {result}")
        
        evaluation_results.append({
            "plant": plant,
            "status": "OK",
            "result": result,
            "explanation": explanation
        })
        
        # Sleep briefly to avoid rate limiting
        time.sleep(1)
    
    return evaluation_results

def run_benchmark():
    """Run the benchmark on all plants in the plants.txt file."""
    timestamp = get_timestamp()
    results_file = RESULTS_FILE.format(timestamp)
    
    print(f"Starting benchmark at {timestamp}")
    print(f"Will use {PHI3_MODEL_NAME} for evaluation")
    
    # Check if plants file exists
    if not os.path.exists(PLANTS_FILE):
        print(f"Error: Plants file {PLANTS_FILE} not found.")
        return
        
    # Create instructions directory if it doesn't exist
    os.makedirs(INSTRUCTIONS_DIR, exist_ok=True)
    
    # Read plants from file
    with open(PLANTS_FILE, 'r') as f:
        plants = [line.strip() for line in f.readlines() if line.strip()]
    
    # Phase 1: Generate instructions
    generate_all_instructions(plants)
    
    # Phase 2: Evaluate instructions
    evaluation_results = evaluate_all_instructions(plants)
    
    # Generate report
    passed = [r for r in evaluation_results if r["result"] == "PASS"]
    failed = [r for r in evaluation_results if r["result"] == "FAIL"]
    errors = [r for r in evaluation_results if r["result"] not in ["PASS", "FAIL"]]
    
    pass_rate = len(passed) / len(plants) * 100 if plants else 0
    
    # Write report to file
    with open(results_file, 'w') as f:
        f.write(f"# Plant Care Benchmark Results\n\n")
        f.write(f"Timestamp: {timestamp}\n\n")
        f.write(f"Evaluation model: {PHI3_MODEL_NAME}\n\n")
        f.write(f"Total plants tested: {len(plants)}\n")
        f.write(f"Passed: {len(passed)} ({pass_rate:.1f}%)\n")
        f.write(f"Failed: {len(failed)}\n")
        f.write(f"Errors: {len(errors)}\n\n")
        
        f.write("## Detailed Results\n\n")
        for r in evaluation_results:
            f.write(f"### {r['plant']}\n")
            f.write(f"Result: {r['result']}\n")
            if "explanation" in r:
                f.write(f"Explanation: {r['explanation']}\n\n")
            else:
                f.write(f"Reason: {r.get('reason', 'Unknown')}\n\n")
    
    # Print summary
    print("\n\n" + "="*50)
    print(f"BENCHMARK SUMMARY ({timestamp})")
    print("="*50)
    print(f"Evaluation model: {PHI3_MODEL_NAME}")
    print(f"Total plants tested: {len(plants)}")
    print(f"Passed: {len(passed)} ({pass_rate:.1f}%)")
    print(f"Failed: {len(failed)}")
    print(f"Errors: {len(errors)}")
    print(f"\nDetailed results written to {results_file}")

if __name__ == "__main__":
    print("Starting plant care benchmark...")
    run_benchmark() 