import os, sys
import json
from utils import chat_gpt, get_client
from config_loader import load_config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import traceback
# Load configuration
config = load_config()

import json

def get_eval_prompt(user_input, model_output):
    prompt = f"""

You are an expert evaluator of AI-generated content. Your task is to evaluate the quality of the output based on the input provided. Your evaluation must strictly follow the JSON structure with the following format:

```json
{{
    "evaluation": {{
        "keywords_quality": <integer>, // Score (1-100)
        "relevance": <integer>,       // Score (1-100)
        "hallucination": <integer>,   // Score (1-100)
        "overall_quality": <integer>  // Score (1-100)
    }},
    "explanation": "<string>"         // Detailed explanation of the evaluation
}}

### Input:
{json.dumps(user_input, indent=4)}

### Output:
{json.dumps(model_output, indent=4)}

### Evaluation Criteria:
1. **Keywords Quality**:
   - How well do the keywords in the output match the profession and background provided in the input?
   - Score (1-100): Based on how accurate and relevant the keywords are.

2. **Relevance**:
   - How relevant is the generated profile (elevator pitch and About Me) to the profession and background provided in the input?
   - Score (1-100): Based on the alignment of the generated content to the input.

3. **Hallucination**:
   - How much does the output invent or hallucinate information not present or implied in the input?
   - Score (1-100): Lower score indicates higher hallucination (less reliable output).

4. **Overall Quality**:
   - General assessment of the output's coherence, fluency, and alignment with the input.
   - Score (1-100): Consider the overall quality and usefulness of the output.

### Examples of JSON Output:

#### High-Quality Example:
Input:
{{
    "profession": "Product Manager",
    "experience_level": "senior",
    "keywords": [
        "Machine Learning",
        "Deep Learning",
        "AI"
    ],
    "background": "Industry expert with over 10 years of experience in software engineering.",
    "similarity_score_input": 60
}}

Output:
{{
    "elevator_pitch": "As a seasoned product manager with a strong foundation in software engineering and a deep understanding of cutting-edge technologies like Deep Learning, AI, and Machine Learning, I drive innovation and deliver top-notch solutions that exceed customer expectations.",
    "About Me": "With over a decade of experience in software engineering, I have honed my skills in product management to lead cross-functional teams in developing successful products rooted in advanced technologies such as Deep Learning, AI, and Machine Learning. My passion for leveraging data-driven insights and market trends allows me to create impactful strategies that drive business growth and foster customer satisfaction. I thrive in dynamic environments where creativity and innovation are valued, and I am committed to continuously pushing boundaries and delivering exceptional results.",
    "retrieved_keywords": [
        "Deep Learning",
        "AI",
        "Machine Learning"
    ],
    "reason": "The elevator pitch and 'About Me' section align with the provided background of being an industry expert with over 10 years of experience in software engineering by highlighting expertise in cutting-edge technologies like Deep Learning, AI, and Machine Learning and showcasing a track record of driving innovation and delivering top-notch solutions.",
    "similarity_scores": {{
        "min_score": 105.57035827636719,
        "max_score": 288.8236083984375
    }}
}}

Your output: 
{{
    "evaluation": {{
        "keywords_quality": 95,
        "relevance": 92,
        "hallucination": 90,
        "overall_quality": 93
    }},
    "explanation": "The keywords are highly relevant to the profession and background. The profile aligns well with the input, with minimal hallucination and an excellent overall quality."
}}

#### Medium-Quality Example:
Input:
{{
    "profession": "UX Designer",
    "experience_level": "mid-level",
    "keywords": [
        "User Research",
        "Prototyping"
    ],
    "background": "Creative thinker with experience in design strategy.",
    "similarity_score_input": 50
}}

Output:
{{
    "elevator_pitch": "As a UX Designer, I excel at delivering user-centered solutions by leveraging my expertise in prototyping and design tools.",
    "About Me": "With experience in user research, I aim to create innovative designs. My passion for design strategy has driven me to develop impactful products for users.",
    "retrieved_keywords": [
        "User Research",
        "Prototyping",
        "Design Tools"
    ],
    "reason": "The output captures some relevant keywords but lacks depth in connecting them to the provided background and profession.",
    "similarity_scores": {{
        "min_score": 90.123456789,
        "max_score": 200.567891234
    }}
}}


Your output: 
{{
    "evaluation": {{
        "keywords_quality": 70,
        "relevance": 75,
        "hallucination": 60,
        "overall_quality": 68
    }},
    "explanation": "The keywords are somewhat relevant but could be improved. The relevance to the input is moderate, and there is some minor hallucination. Overall quality is average."
}}

#### Low-Quality Example:
Input:
{{
    "profession": "Data Analyst",
    "experience_level": "entry-level",
    "keywords": [
        "SQL",
        "Excel",
        "Data Visualization"
    ],
    "background": "Recent graduate with coursework in data analytics.",
    "similarity_score_input": 40
}}

Output:
{{
    "elevator_pitch": "I am a data enthusiast who loves working with numbers and creating beautiful charts using Photoshop and Canva.",
    "About Me": "My passion for design and numbers allows me to excel in presenting data-driven stories.",
    "retrieved_keywords": [
        "Photoshop",
        "Canva"
    ],
    "reason": "The output fails to align with the provided background and profession, and includes irrelevant keywords such as 'Photoshop' and 'Canva'.",
    "similarity_scores": {{
        "min_score": 70.123,
        "max_score": 150.456
    }}
}}

Your output:

{{
    "evaluation": {{
        "keywords_quality": 40,
        "relevance": 30,
        "hallucination": 20,
        "overall_quality": 35
    }},
    "explanation": "The keywords are largely irrelevant, the profile does not align well with the input, and there is significant hallucination. Overall quality is poor."
}}
"""
    return prompt


def evaluate_output(input_file, output_file, client, output_dir):
    """
    Evaluate the quality of output based on input using ChatGPT.

    Args:
        input_file (str): Path to the input JSON file.
        output_file (str): Path to the output JSON file.
        client (OpenAI): Initialized OpenAI client.
        output_dir (str): Directory to save the evaluation results.

    Returns:
        None
    """
    try:
        with open(input_file, "r") as infile, open(output_file, "r") as outfile:
            user_input = json.load(infile)
            model_output = json.load(outfile)

        # Construct prompt
        prompt = get_eval_prompt(user_input, model_output)

        # Call ChatGPT
        evaluation = chat_gpt(prompt, client, model="gpt-4")

        # Parse evaluation as JSON
        try:
            evaluation_data = json.loads(evaluation)
        except json.JSONDecodeError:
            print(f"Error: Unable to parse ChatGPT response as JSON. Response:\n{evaluation}")
            return

        # Save evaluation
        os.makedirs(output_dir, exist_ok=True)
        evaluation_file = os.path.join(output_dir, f"evaluation_{os.path.basename(input_file)}")
        with open(evaluation_file, "w") as eval_file:
            json.dump(evaluation_data, eval_file, indent=4)
        print(f"Evaluation saved to: {evaluation_file}")

    except Exception as e:
        print(f"Error evaluating input/output pair: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    output_dir = os.path.join(config["paths"]["output_dir"], "generate_profile")
    input_dir = os.path.join(config["paths"]["input_dir"], "generate_profile")
    evaluation_dir = os.path.join(config["paths"]["output_dir"], "evaluate_profile_generation")
    client = get_client()  
    input_files = sorted([f for f in os.listdir(input_dir) if f.endswith(".json")])
    output_files = sorted([f for f in os.listdir(output_dir) if f.endswith(".json")])
    print(f"Found {len(input_files)} input files, {len(output_files)} output files")
    if len(input_files) != len(output_files):
        print("Error: The number of input and output files must match.")
    else:
        for input_file, output_file in zip(input_files, output_files):
            input_path = os.path.join(input_dir, input_file)
            output_path = os.path.join(output_dir, output_file)
            evaluate_output(input_path, output_path, client, evaluation_dir)
