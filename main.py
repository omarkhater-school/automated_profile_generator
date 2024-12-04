from flask import Flask, render_template, request, jsonify
from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document
import time
from config_loader import load_config
from utils import get_vectorstore, get_client, retrieve_skills_from_chroma, generate_profile

# Initialize Flask app
app = Flask(__name__)
# Load configuration
config = load_config("config.yml")
embedding_model = config['settings']['embedding_model']
persist_directory = config['paths']['persist_directory']

# Initialize Chroma vectorstore
vectorstore = get_vectorstore()
client = get_client()

@app.route('/')
def home():
    """Render the homepage."""
    return render_template('index.html')

@app.route('/api/generate-profile', methods=['POST'])
def generate_user_profile():
    """API endpoint to generate a professional profile."""
    try:
        user_input = request.json
        start_time = time.time()
        profile = generate_profile(user_input, vectorstore, client)
        end_time = time.time()

        response = {
            "profile": profile,
            "stats": {
                "time_taken": round(end_time - start_time, 2)
            }
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/retrieve-skills', methods=['POST'])
def retrieve_skills():
    """API endpoint to retrieve trending skills."""
    try:
        profession = request.json.get("profession")
        keywords = retrieve_skills_from_chroma(profession)
        return jsonify({"keywords": keywords})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
