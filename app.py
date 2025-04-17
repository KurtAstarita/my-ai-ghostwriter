import google.generativeai as genai
from flask import Flask, request, jsonify, session, render_template, abort
from AiGhostWriter import get_gemini_flash_output, transform_to_human_like
from flask_cors import CORS
import os
import logging
import bleach
from flask_wtf.csrf import CSRFProtect, generate_csrf, ValidationError # We'll remove CSRFProtect for now
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or 'your_fallback_secret_key'
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "https://myaighostwriter.kurtastarita.com"}})
# csrf = CSRFProtect(app) # Removing Flask-WTF CSRF for now
limiter = Limiter(get_remote_address, app=app, storage_uri="memory://")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
allowed_tags = ['p', 'br', 'span']
allowed_attributes = {}

GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
gemini_model = None

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-2.0-flash')
else:
    logger.error("GOOGLE_API_KEY environment variable not set!")

signer = URLSafeTimedSerializer(app.secret_key)
CSRF_TOKEN_NAME = 'csrf_token'
CSRF_HEADER_NAME = 'X-CSRF-Token'

def generate_stateless_csrf_token():
    session_id = session.get('session_id') # Assuming you have a session ID
    if not session_id:
        session['session_id'] = os.urandom(16).hex()
        session_id = session['session_id']
    return signer.dumps({'sid': session_id})

def verify_stateless_csrf_token(token):
    session_id = session.get('session_id')
    if not session_id:
        return False
    try:
        data = signer.loads(token, max_age=3600)
        return data.get('sid') == session_id
    except Exception as e:
        logger.warning(f"CSRF verification failed: {e}")
        return False

@app.route('/csrf_token', methods=['GET'])
def get_csrf_token():
    token = generate_stateless_csrf_token()
    return jsonify({CSRF_TOKEN_NAME: token})

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/generate', methods=['POST'])
@limiter.limit("5 per minute")
def generate_content():
    logger.info(f"Cookies in /generate: {request.cookies}")
    logger.info(f"Session ID in /generate before verification: {session.get('session_id')}")
    csrf_token_from_header = request.headers.get(CSRF_HEADER_NAME)
    logger.info(f"CSRF Token from header: {csrf_token_from_header}")
    if not verify_stateless_csrf_token(csrf_token_from_header):
        logger.warning("CSRF token verification failed for /generate")
        return jsonify({'error': 'Invalid CSRF token'}), 403

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

        ai_output = get_gemini_flash_output(backstory, samples, prompt, gemini_model)
        human_like_output = transform_to_human_like(ai_output, samples)

        return jsonify({'generated_content': human_like_output})

    except Exception as e:
        logger.error(f"An error occurred during content generation: {e}")
        return jsonify({'error': 'An unexpected error occurred on the server.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
