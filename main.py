from flask import Flask, render_template, request, jsonify
from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document
import time
from config_loader import load_config
from utils import get_vectorstore, get_client, retrieve_skills_from_chroma, generate_profile, chat_gpt

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

@app.route('/social-profile-upgrade')
def social_profile_upgrade():
    """Render the Social Media Profile Upgrade page."""
    return render_template('social-profile-upgrade.html')

@app.route('/resume-upgrade')
def resume_upgrade():
    """Render the Resume Upgrade page."""
    print("Rendering resume upgrade")
    return render_template('resume-upgrade.html')

@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    """Handle feedback submissions."""
    try:
        data = request.get_json()  # Retrieve JSON payload
        stars = data.get("stars")
        comments = data.get("comments")
        
        # Log the received feedback
        print(f"Received feedback: {stars} stars, Comment: {comments}")

        # Return a success response
        return jsonify({"message": "Feedback submitted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



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
        print("Response being sent:", response)
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

@app.route('/api/health-check', methods=['GET'])
def health_check():
    """API endpoint to check the health of the system."""
    try:
        health_status = {}

        # Check vector store health
        try:
            vectorstore_test_query = vectorstore.similarity_search("Machine Learning Engineer", k=1)
            health_status["vector_store"] = {
                "status": "healthy",
                "message": f"Vector store contains {len(vectorstore_test_query)} results for test query."
            }
        except Exception as e:
            health_status["vector_store"] = {
                "status": "unhealthy",
                "message": str(e)
            }

        # Check model availability
        try:
            prompt = "Test prompt for model health check."
            model_response = chat_gpt(prompt, client)
            health_status["model"] = {
                "status": "healthy",
                "message": "Model responded successfully."
            }
        except Exception as e:
            health_status["model"] = {
                "status": "unhealthy",
                "message": str(e)
            }

        # Check configuration
        try:
            config_check = load_config()
            health_status["configuration"] = {
                "status": "healthy",
                "message": "Configuration loaded successfully."
            }
        except Exception as e:
            health_status["configuration"] = {
                "status": "unhealthy",
                "message": str(e)
            }

        return jsonify({"health": health_status}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
