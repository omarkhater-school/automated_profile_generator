import os
import json
import pandas as pd
from config_loader import load_config

def combine_json_to_csv(input_dir, output_dir, evaluation_dir, output_csv):
    """
    Combines input, output, and evaluation JSON files into a single CSV file.

    Args:
        input_dir (str): Directory containing input JSON files.
        output_dir (str): Directory containing output JSON files.
        evaluation_dir (str): Directory containing evaluation JSON files.
        output_csv (str): Path to the resulting CSV file.
    """
    rows = []

    # Load input, output, and evaluation files
    input_files = sorted([f for f in os.listdir(input_dir) if f.endswith(".json")])
    output_files = sorted([f for f in os.listdir(output_dir) if f.endswith(".json")])
    evaluation_files = sorted([f for f in os.listdir(evaluation_dir) if f.endswith(".json")])

    if not (len(input_files) == len(output_files) == len(evaluation_files)):
        print("Error: Input, output, and evaluation files count do not match.")
        return

    for input_file, output_file, evaluation_file in zip(input_files, output_files, evaluation_files):
        try:
            # Read JSON files
            with open(os.path.join(input_dir, input_file), "r") as infile:
                input_data = json.load(infile)
            with open(os.path.join(output_dir, output_file), "r") as outfile:
                output_data = json.load(outfile)
            with open(os.path.join(evaluation_dir, evaluation_file), "r") as evalfile:
                evaluation_data = json.load(evalfile)

            # Extract fields for the CSV
            row = {
                "Input File": input_file,
                "Profession": input_data.get("profession", ""),
                "Experience Level": input_data.get("experience_level", ""),
                "Keywords": ", ".join(input_data.get("keywords", [])),
                "Background": input_data.get("background", ""),
                "Similarity Score Input": input_data.get("similarity_score_input", ""),
                "Elevator Pitch": output_data.get("elevator_pitch", ""),
                "About Me": output_data.get("About Me", ""),
                "Retrieved Keywords": ", ".join(output_data.get("retrieved_keywords", [])),
                "Evaluation Keywords Quality": evaluation_data["evaluation"].get("keywords_quality", ""),
                "Evaluation Relevance": evaluation_data["evaluation"].get("relevance", ""),
                "Evaluation Hallucination": evaluation_data["evaluation"].get("hallucination", ""),
                "Evaluation Overall Quality": evaluation_data["evaluation"].get("overall_quality", ""),
                "Evaluation Explanation": evaluation_data.get("explanation", "")
            }

            rows.append(row)

        except Exception as e:
            print(f"Error processing files: {input_file}, {output_file}, {evaluation_file}")
            print(f"Error: {e}")
            continue

    # Create DataFrame and save to CSV
    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False)
    print(f"CSV file created: {output_csv}")

if __name__ == "__main__":
    # Load configuration
    config = load_config()
    
    # Directories
    input_dir = os.path.join(config["paths"]["input_dir"], "generate_profile")
    output_dir = os.path.join(config["paths"]["output_dir"], "generate_profile")
    evaluation_dir = os.path.join(config["paths"]["output_dir"], "evaluate_profile_generation")
    output_csv = os.path.join(config["paths"]["output_dir"], "API_evaluation_by_ai.csv")

    # Combine JSON files to CSV
    combine_json_to_csv(input_dir, output_dir, evaluation_dir, output_csv)
