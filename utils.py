import requests
from bs4 import BeautifulSoup
from langchain_chroma import Chroma
from langchain_community.embeddings.ollama import OllamaEmbeddings
from openai import OpenAI
from config_loader import load_config

def chat_gpt(prompt, client):
    """
    Generates a response using GPT-3.5 Turbo.
    
    Args:
        prompt (str): The input prompt for GPT.
        client (OpenAI): An initialized OpenAI client.
    
    Returns:
        str: The generated content from GPT.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in chat_gpt: {e}")
        return ""

def fetch_trending_keywords(profession, headers, max_keywords=10):
    """
    Fetch trending keywords for a given profession.

    Args:
        profession (str): The profession to fetch keywords for.
        headers (dict): Headers for the HTTP request.
        max_keywords (int): Maximum number of keywords to fetch.

    Returns:
        list: A list of trending keywords.
    """
    try:
        search_url = f"https://www.google.com/search?q=trending+skills+for+{profession.replace(' ', '+')}"
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        keywords = [suggestion.text for suggestion in soup.select("div.B0jnne")]

        return list(set(keywords))[:max_keywords]
    except Exception as e:
        print(f"Error fetching trending keywords for {profession}: {e}")
        return []

def retrieve_skills_from_chroma(profession, vectorstore, threshold= 1e-5):
    """
    Retrieve trending skills from ChromaDB for a given profession.

    Args:
        profession (str): The profession to search for.
        vectorstore (Chroma): The initialized ChromaDB instance.
        threshold (float): Minimum acceptable relevance score.

    Returns:
        list: A list of trending keywords, or an empty list if none found.
    """
    try:
        results = vectorstore.similarity_search_with_score(profession, k=50)
        print(f"Results from similarity search: {results}")

        fetched_keywords = []

        for result, similarity_score in results:
            # Convert similarity score to relevance score
            relevance_score = 1 / (1 + similarity_score)
            print(f"Similarity Score: {similarity_score:5f}, Relevance Score: {relevance_score:5f}, thresold: {threshold}")

            # Filter based on the relevance score threshold
            if relevance_score >= threshold:
                keywords = eval(result.metadata.get('trending_keywords', '[]'))
                fetched_keywords.extend(keywords)

        # Deduplicate keywords and return
        return list(set(fetched_keywords))
    except Exception as e:
        print(f"Error retrieving skills from ChromaDB: {e}")
        return []


def generate_profile(user_input, vectorstore, client):
    """
    Generate a professional profile using user input and ChromaDB.

    Args:
        user_input (dict): Dictionary with keys `profession`, `experience_level`, `keywords`, and optionally `background`.
        vectorstore (Chroma): Initialized ChromaDB instance.
        client (OpenAI): Initialized OpenAI client.

    Returns:
        dict: Generated elevator pitch and project descriptions.
    """
    profession = user_input.get("profession", "a professional")
    experience_level = user_input.get("experience_level", "mid-level")
    user_keywords = user_input.get("keywords", [])
    background = user_input.get("background", "").strip()  # Optional user-provided background

    trending_keywords = retrieve_skills_from_chroma(profession, vectorstore)
    if not trending_keywords:
        print(f"Fetching trending keywords for {profession}...")
        headers = {"User-Agent": user_input.get("headers")}
        trending_keywords = fetch_trending_keywords(profession, headers)
        print(f"Trending keywords: {trending_keywords}")

    all_keywords = list(set(user_keywords + trending_keywords))
    keywords_str = ", ".join(all_keywords) if all_keywords else "relevant skills and expertise"

    if background:
        prompt = (
            f"Craft a highly engaging and personalized elevator pitch and a LinkedIn 'About Me' section for {profession}. "
            f"The individual is a {experience_level} professional with the following background:\n{background}\n\n"
            f"Use keywords such as {keywords_str}. Ensure the tone is confident, professional, and aspirational. "
            f"Do not fabricate any details but fully utilize the provided background information and keywords. "
            f"Focus on their professional expertise, unique qualities, and career goals. "
            f"Make the profile appealing to recruiters, clients, and colleagues."
        )
    else:
        prompt = (
            f"Craft a highly engaging and personalized elevator pitch and a LinkedIn 'About Me' section for {profession}. "
            f"The individual is a {experience_level} professional. "
            f"Use keywords such as {keywords_str}. Ensure the tone is confident, professional, and aspirational. "
            f"Since no specific background information is provided, focus on the keywords and profession to generate a relevant profile. "
            f"Highlight professional expertise, potential unique qualities, and likely career goals. "
            f"Make the profile appealing to recruiters, clients, and colleagues."
        )

    try:
        generated_text = chat_gpt(prompt, client)
        return {
            "elevator_pitch": generated_text.split("\n\n")[0],
            "About Me": "\n\n".join(generated_text.split("\n\n")[1:]),
            "retrieved_keywords": ", ".join(trending_keywords)
        }
    except Exception as e:
        print(f"Error generating profile: {e}")
        return {"error": str(e)}

    
def get_vectorstore():
    """
    Initialize and return the Chroma vectorstore.

    Returns:
        Chroma: An initialized Chroma vectorstore instance.
    """
    config = load_config("config.yml")
    embedding_model = config['settings']['embedding_model']
    persist_directory = config['paths']['persist_directory']

    embedding = OllamaEmbeddings(model=embedding_model)
    vectorstore = Chroma(
        collection_name=config['settings']['collection_name'],
        embedding_function=embedding,
        persist_directory=persist_directory,
    )
    return vectorstore


def get_client():
    """
    Initialize and return the OpenAI client.

    Returns:
        OpenAI: An initialized OpenAI client instance.
    """
    from config import open_ai_api_key  # Import API key from config
    client = OpenAI(api_key=open_ai_api_key)
    return client
