from flask import Flask, request, jsonify, make_response
from AiGhostWriter import get_gemini_flash_output, transform_to_human_like, model
from flask_cors import CORS
import os
import logging
import bleach
from flask_wtf.csrf import CSRFProtect # Import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or 'your_fallback_secret_key'
CORS(app)
csrf = CSRFProtect(app) # Initialize CSRF protection
limiter = Limiter(get_remote_address, app=app, storage_uri="memory://")

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
allowed_tags = ['p', 'br', 'span']
allowed_attributes = {}

@app.route('/')
def hello_world():
    response = make_response('Hello, World!')
    csrf_token = csrf.generate_csrf()
    response.set_cookie('csrf_token', csrf_token, httponly=True, secure=True, samesite='Strict')
    return response

@app.route('/generate', methods=['POST'])
@limiter.limit("5 per minute")
def generate_content():
    try:
        data = request.get_json()
        backstory = data.get('backstory')
        samples = data.get('samples')
        prompt = data.get('prompt')

        if not backstory or not samples or not prompt:
            return jsonify({'error': 'Missing required data (backstory, samples, or prompt)'}), 400

        backstory = bleach.clean(backstory, tags=allowed_tags, attributes=allowed_attributes, strip=True)
        samples = bleach.clean(samples, tags=allowed_tags, attributes=allowed_attributes, strip=True)
        prompt = bleach.clean(prompt, tags=allowed_tags, attributes=allowed_attributes, strip=True)

        ai_output = get_gemini_flash_output(backstory, samples, prompt)
        human_like_output = transform_to_human_like(ai_output, samples)

        return jsonify({'generated_content': human_like_output})

    except Exception as e:
        logger.error(f"An error occurred during content generation: {e}")
        return jsonify({'error': 'An unexpected error occurred on the server.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
