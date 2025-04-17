import google.generativeai as genai
from flask import Flask, request, jsonify, session
from AiGhostWriter import get_gemini_flash_output, transform_to_human_like
from flask_cors import CORS
import os
import logging
import bleach
# from flask_wtf.csrf import CSRFProtect, generate_csrf, ValidationError # Comment out import
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or 'your_fallback_secret_key'
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "https://myaighostwriter.kurtastarita.com"}})
srf = CSRFProtect(app)
limiter = Limiter(get_remote_address, app=app, storage_uri="memory://")

logging.basicConfig(level=logging.INFO) # Set logging level to INFO
logger = logging.getLogger(__name__)
allowed_tags = ['p', 'br', 'span']
allowed_attributes = {}

# Use environment variable for Google API Key
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
gemini_model = None # Initialize gemini_model here

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    # Initialize the Gemini model here
    gemini_model = genai.GenerativeModel('gemini-2.0-flash')
else:
    logger.error("GOOGLE_API_KEY environment variable not set!")
    # Potentially return an error response if the API key is crucial

from flask_wtf.csrf import csrf # Make sure this is imported

@app.route('/csrf_token', methods=['GET'])
@csrf.exempt # Exempt this route from CSRF protection
def get_csrf_token():
    token = generate_csrf()
    session['_csrf_token'] = token
    return jsonify({'csrf_token': token})

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/generate', methods=['POST'])
@limiter.limit("5 per minute")
@csrf.protect() # Protect this route against CSRF
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

        referer = request.headers.get('Referer')
        allowed_origins = ["https://kurtastarita.github.io/", "https://myaighostwriter.kurtastarita.com/"]
        if referer and not any(referer.startswith(origin) for origin in allowed_origins):
            logger.warning(f"Suspicious Referer header: {referer}")
            return jsonify({'error': 'Invalid Referer header'}), 403

        backstory = bleach.clean(backstory, tags=allowed_tags, attributes=allowed_attributes, strip=True)
        samples = bleach.clean(samples, tags=allowed_tags, attributes=allowed_attributes, strip=True)
        prompt = bleach.clean(prompt, tags=allowed_tags, attributes=allowed_attributes, strip=True)

        # Get the raw AI output
        ai_output = get_gemini_flash_output(backstory, samples, prompt, gemini_model)

        # Transform the AI output to be more human-like
        human_like_output = transform_to_human_like(ai_output, samples)

        return jsonify({'generated_content': human_like_output})

    except Exception as e:
        logger.error(f"An error occurred during content generation: {e}")
        return jsonify({'error': 'An unexpected error occurred on the server.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
