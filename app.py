from flask import Flask, request, jsonify
from AiGhostWriter import get_gemini_flash_output, transform_to_human_like, model
from flask_cors import CORS
import os
import logging
import bleach # Import the bleach library

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or 'your_fallback_secret_key'
CORS(app)

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Define allowed tags and attributes for sanitization (customize as needed)
allowed_tags = ['p', 'br', 'span']
allowed_attributes = {}

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/generate', methods=['POST'])
def generate_content():
    try:
        data = request.get_json()
        backstory = data.get('backstory')
        samples = data.get('samples')
        prompt = data.get('prompt')

        if not backstory or not samples or not prompt:
            return jsonify({'error': 'Missing required data (backstory, samples, or prompt)'}), 400

        # Sanitize the inputs
        backstory = bleach.clean(backstory, tags=allowed_tags, attributes=allowed_attributes, strip=True)
        samples = bleach.clean(samples, tags=allowed_tags, attributes=allowed_attributes, strip=True)
        prompt = bleach.clean(prompt, tags=allowed_tags, attributes=allowed_attributes, strip=True)

        # Get the initial AI output using Gemini
        ai_output = get_gemini_flash_output(backstory, samples, prompt)

        # Transform the AI output to sound more human-like
        human_like_output = transform_to_human_like(ai_output, samples)

        # Return the transformed output as JSON
        return jsonify({'generated_content': human_like_output})

    except Exception as e:
        logger.error(f"An error occurred during content generation: {e}")
        return jsonify({'error': 'An unexpected error occurred on the server.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
