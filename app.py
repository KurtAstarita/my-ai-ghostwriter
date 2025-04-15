from flask import Flask, request, jsonify, session
from AiGhostWriter import get_gemini_flash_output, transform_to_human_like, model
from flask_cors import CORS
import os
import logging
import bleach
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or 'your_fallback_secret_key'
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "https://kurtastarita.github.io"}})
app.config['SESSION_COOKIE_DOMAIN'] = 'my-ai-ghostwriter.onrender.com' # Set to your backend domain
csrf = CSRFProtect(app) # Initialize CSRF protection
limiter = Limiter(get_remote_address, app=app, storage_uri="memory://")

logging.basicConfig(level=logging.INFO) # Set logging level to INFO
logger = logging.getLogger(__name__)
allowed_tags = ['p', 'br', 'span']
allowed_attributes = {}

@app.route('/csrf_token', methods=['GET'])
def get_csrf_token():
    token = generate_csrf()
    session['_csrf_token'] = token # Store the token in the session
    return jsonify({'csrf_token': token})

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/generate', methods=['POST'])
@limiter.limit("5 per minute")
def generate_content():
    try:
        logger.info("Processing /generate request")
        logger.info(f"Request Headers: {request.headers}")
        data = request.get_json()
        backstory = data.get('backstory')
        samples = data.get('samples')
        prompt = data.get('prompt')

        if not backstory or not samples or not prompt:
            logger.warning("Missing required data")
            return jsonify({'error': 'Missing required data (backstory, samples, or prompt)'}), 400

        csrf.validate_csrf(request.headers.get('X-CSRFToken'))
        logger.info("CSRF validation successful")

        backstory = bleach.clean(backstory, tags=allowed_tags, attributes=allowed_attributes, strip=True)
        samples = bleach.clean(samples, tags=allowed_tags, attributes=allowed_attributes, strip=True)
        prompt = bleach.clean(prompt, tags=allowed_tags, attributes=allowed_attributes, strip=True)

        ai_output = get_gemini_flash_output(backstory, samples, prompt)
        human_like_output = transform_to_human_like(ai_output, samples)

        return jsonify({'generated_content': human_like_output})

    except ValidationError as e:
        logger.warning(f"CSRF validation failed: {e}")
        return jsonify({'error': 'CSRF token validation failed'}), 400
    except Exception as e:
        logger.error(f"An error occurred during content generation: {e}")
        return jsonify({'error': 'An unexpected error occurred on the server.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
