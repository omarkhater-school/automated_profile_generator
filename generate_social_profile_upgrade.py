import os
import sys
import json
import datetime
import logging
import traceback
import random
from config_loader import load_config
from utils import get_client, get_vectorstore
from utils import generate_profile

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load configuration
config = load_config()


class InfoFilter(logging.Filter):
    """
    Logging filter to allow only INFO level messages.
    """
    def filter(self, record):
        return record.levelno == logging.INFO


def setup_logger(log_dir):
    """
    Set up the logger with a file handler and console handler.

    Args:
        log_dir (str): Directory where log files will be stored.

    Returns:
        logging.Logger: Configured logger instance.
    """
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(
        log_dir, f"profile_eval_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(levelname)s: %(message)s")
    console_handler.setFormatter(console_formatter)
    console_handler.addFilter(InfoFilter())

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Initialize logger
log_dir = os.path.join(config["paths"]["logs_dir"], "profile_eval_logs")
logger = setup_logger(log_dir)


def generate_user_inputs(n=5):
    """
    Generate a diverse set of user inputs for profile generation.

    Args:
        n (int): Number of user input dictionaries to generate.

    Returns:
        list: A list of dictionaries with user input parameters.
    """
    professions = [
        "Data Scientist", 
        "Software Engineer", 
        "Product Manager", 
        "UX Designer", 
        "Marketing Specialist",
        "Machine Learning Engineer",
        "DevOps Engineer",
        "Blockchain Developer",
        "Cybersecurity Analyst",
        "Business Intelligence Analyst"
    ]

    experience_levels = [
        "entry-level", 
        "mid-level", 
        "senior"
    ]

    keywords = [
        ["AI", "Machine Learning", "Deep Learning"], 
        ["Frontend", "React", "JavaScript"], 
        ["Agile", "Scrum", "Project Management"], 
        ["User Research", "Prototyping", "Usability Testing"], 
        ["SEO", "Content Marketing", "Analytics"],
        ["Cloud Computing", "AWS", "DevOps"],
        ["Blockchain", "Smart Contracts", "Cryptography"],
        ["Cybersecurity", "Risk Assessment", "Penetration Testing"],
        ["Data Visualization", "SQL", "Python"],
        ["Mobile Development", "Swift", "Kotlin"]
    ]

    backgrounds = [
        "Graduate from a top university with a passion for technology.",
        "Graduate from TAMU with a passion for marketing.",
        "Experienced professional with a strong foundation in data analytics.",
        "Creative thinker with expertise in visual storytelling.",
        "Graduate with a Master's in Computer Science from TAMU.",
        "Industry expert with over 10 years of experience in software engineering.",
        "Self-taught programmer passionate about open-source contributions.",
        "Graduate from NYU with a focus on human-computer interaction.",
        "Digital marketing specialist with a proven track record in SEO.",
        "Cloud computing enthusiast with AWS certification.",
        "Entry-level data scientist with strong statistical analysis skills."
    ]

    similarity_scores = [20, 30, 40, 50, 60, 70, 80, 90]

    user_inputs = []
    for _ in range(n):
        user_inputs.append({
            "profession": random.choice(professions),
            "experience_level": random.choice(experience_levels),
            "keywords": random.sample(random.choice(keywords), random.randint(2, 3)),
            "background": random.choice(backgrounds),
            "similarity_score_input": random.choice(similarity_scores),
        })

    return user_inputs


def save_results(base_dir, subfolder, file_name, content):
    """
    Save the results to a JSON file in the specified directory and subfolder.

    Args:
        base_dir (str): Base directory to save the results.
        subfolder (str): Subfolder within the base directory (e.g., 'generate_profile').
        file_name (str): Name of the output file.
        content (dict): Content to save.
    """
    try:
        # Construct the target directory path
        target_dir = os.path.join(base_dir, subfolder)
        os.makedirs(target_dir, exist_ok=True)

        # Create the file path and save the content
        output_file = os.path.join(target_dir, f"{file_name}.json")
        with open(output_file, "w") as f:
            json.dump(content, f, indent=4)
        logger.info(f"Saved results to {output_file}")
    except Exception as e:
        logger.error(f"Error saving results to {target_dir}: {e}")

if __name__ == "__main__":
    output_dir = config["paths"]["output_dir"]
    input_dir = config["paths"]["input_dir"]
    vectorstore = get_vectorstore()
    client = get_client()

    user_inputs = generate_user_inputs(n=15)

    for idx, user_input in enumerate(user_inputs, start=1):
        try:
            logger.info(f"Processing user input {idx} of {len(user_inputs)}...")

            # Save user input to the input directory under 'generate_profile' subfolder
            input_file_name = f"user_input_{idx:03d}"
            save_results(input_dir, "generate_profile", input_file_name, user_input)

            # Generate the profile
            profile = generate_profile(user_input, vectorstore, client)

            # Save the profile results to the output directory under 'generate_profile' subfolder
            output_file_name = f"profile_{idx:03d}"
            save_results(output_dir, "generate_profile", output_file_name, profile)

            # Log similarity scores and responses
            similarity_scores = profile.get("similarity_scores", {})
            logger.info(f"User Input: {user_input}")
            logger.info(f"Generated Profile: {profile}")
            logger.info(f"Similarity Scores: {similarity_scores}")
        except Exception as e:
            logger.error(f"Error processing user input {idx}: {e}")
            traceback.print_exc()
