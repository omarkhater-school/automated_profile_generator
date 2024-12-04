import os
import pandas as pd
from langchain_chroma import Chroma
from langchain.schema import Document
from langchain_community.embeddings.ollama import OllamaEmbeddings
from tqdm import tqdm
from config_loader import load_config


def custom_relevance_score_fn(similarity_score: float) -> float:
    """Custom relevance score function."""
    relevance_score = 1 / (1 + similarity_score)
    return relevance_score


def load_csv_data(file_path, limit=None):
    """Load data from a CSV file."""
    try:
        df = pd.read_csv(file_path)
        if limit:
            df = df.iloc[:limit, :]
        return df
    except Exception as e:
        print(f"Error loading CSV data: {e}")
        return pd.DataFrame()


def prepare_documents(df):
    """Prepare LangChain Document objects from a DataFrame."""
    documents = []
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Converting data to documents"):
        doc = Document(page_content=row['Job Title'], metadata={"Trending Skills": row['Trending Skills']})
        documents.append(doc)
    return documents


def initialize_vectorstore(config, embedding_function, relevance_score_fn):
    """Initialize the Chroma vectorstore."""
    persist_directory = config['paths']['persist_directory']
    os.makedirs(persist_directory, exist_ok=True)
    return Chroma(
        collection_name=config['settings']['collection_name'],
        embedding_function=embedding_function,
        persist_directory=persist_directory,
        relevance_score_fn=relevance_score_fn,
    )


def add_documents_to_vectorstore(vectorstore, documents, batch_size=10):
    """Add documents to the vectorstore in batches."""
    for i in tqdm(range(0, len(documents), batch_size), desc="Adding documents to ChromaDB"):
        batch = documents[i:i + batch_size]
        vectorstore.add_documents(batch)
    print("\nDatabase successfully saved to disk.")


if __name__ == "__main__":
    # Load configuration
    config = load_config()
    
    # Load data
    file_path = config['paths']['job_skills_dataset']
    df_limit = config['settings']['row_limit']
    df = load_csv_data(file_path, limit=df_limit)
    
    # Prepare data
    df['text'] = df['Job Title'] + ": " + df['Trending Skills']
    
    # Initialize embeddings
    embedding = OllamaEmbeddings(model=config['settings']['embedding_model'])
    
    # Initialize ChromaDB
    vectorstore = initialize_vectorstore(config, embedding, custom_relevance_score_fn)
    
    # Convert to LangChain Document objects
    documents = prepare_documents(df)
    
    # Add documents to vectorstore
    add_documents_to_vectorstore(vectorstore, documents, batch_size=config['settings']['batch_size'])
