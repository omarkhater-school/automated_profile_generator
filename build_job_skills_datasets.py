import requests
from bs4 import BeautifulSoup
import pandas as pd
import yaml
import os 
import time
from config_loader import load_config

def load_job_titles(csv_file):
    """Load job titles from a CSV file."""
    try:
        df = pd.read_csv(csv_file)
        return df['Job Title'].tolist()
    except Exception as e:
        print(f"Error loading job titles: {e}")
        return []

def fetch_trending_keywords(profession, headers, max_keywords, max_retries=3, delay=2):
    """
    Fetch trending keywords for a given profession with retry and delay.
    
    Args:
        profession (str): The profession to fetch keywords for.
        headers (dict): Headers for the HTTP request.
        max_keywords (int): Maximum number of keywords to return.
        max_retries (int): Number of retries in case of 429 errors.
        delay (int): Time in seconds to wait between retries.
    
    Returns:
        list: A list of trending keywords.
    """
    for attempt in range(max_retries):
        try:
            # Build the search URL
            search_url = f"https://www.google.com/search?q=trending+skills+for+{profession.replace(' ', '+')}"
            
            # Perform the HTTP GET request
            response = requests.get(search_url, headers=headers)
            
            # Check for 429 status code
            if response.status_code == 429:
                print(f"429 Too Many Requests for {profession}. Retrying in {delay} seconds...")
                time.sleep(delay)
                continue  # Retry the request
            
            # Raise an HTTPError for other status codes
            response.raise_for_status()
            
            # Parse the HTML using BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract keyword suggestions from the search results
            keywords = []
            for suggestion in soup.select("div.B0jnne"):  # Adjust based on Google SERP HTML structure
                keywords.append(suggestion.text)
            
            # Remove duplicates and limit to max_keywords
            return list(set(keywords))[:max_keywords]
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching trending keywords for {profession} (Attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)  # Wait before retrying
            else:
                print(f"Failed to fetch keywords for {profession} after {max_retries} attempts.")
                return []

def build_job_skills_dataset(job_titles, headers, max_keywords):
    """Build a dataset of job titles and corresponding trending skills."""
    dataset = []
    
    for title in job_titles:
        print(f"Fetching trending skills for {title}...")
        skills = fetch_trending_keywords(title, headers, max_keywords)
        
        if skills:
            dataset.append({
                "Job Title": title,
                "Trending Skills": skills
            })
    
    return pd.DataFrame(dataset)

def save_dataset(df, output_file):
    """Save the dataset to a CSV file, creating the directory if it does not exist."""
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Save the DataFrame to a CSV file
        df.to_csv(output_file, index=False)
        print(f"Dataset saved to {output_file}")
    except Exception as e:
        print(f"Error saving dataset: {e}")

import time

if __name__ == "__main__":
    # Load configuration
    config = load_config()
    headers = {"User-Agent": config['settings']['user_agent']}
    max_keywords = config['settings']['max_keywords']
    job_titles_csv = config['paths']['job_titles_csv']
    output_file = config['paths']['job_skills_dataset']
    
    # Load job titles
    job_titles = load_job_titles(job_titles_csv)
    print(f"Loaded {len(job_titles)} job titles.")
    
    # Start timing the data collection process
    start_time = time.time()
    
    # Build dataset
    job_skills_df = build_job_skills_dataset(job_titles, headers, max_keywords)
    
    # End timing the data collection process
    end_time = time.time()
    time_taken = end_time - start_time
    
    # Save dataset
    save_dataset(job_skills_df, output_file)
    
    # Collect stats
    num_jobs_collected = len(job_skills_df)
    total_keywords = sum(len(row.split(", ")) for row in job_skills_df["Trending Skills"] if isinstance(row, str))
    avg_keywords_per_job = total_keywords / num_jobs_collected if num_jobs_collected > 0 else 0
    
    # Print stats
    print("\n=== Data Collection Statistics ===")
    print(f"Time taken: {time_taken:.2f} seconds")
    print(f"Number of jobs collected: {num_jobs_collected}")
    print(f"Total number of keywords collected: {total_keywords}")
    print(f"Average number of keywords per job: {avg_keywords_per_job:.2f}")
    print(f"Dataset saved to: {output_file}")

