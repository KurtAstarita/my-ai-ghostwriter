from flask import Flask, request, jsonify
from AiGhostWriter import get_gemini_flash_output, transform_to_human_like, model
from flask_cors import CORS  # Add this line

app = Flask(__name__)
CORS(app)

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

        # Get the initial AI output using Gemini
        ai_output = get_gemini_flash_output(backstory, samples, prompt)

        # Transform the AI output to sound more human-like
        human_like_output = transform_to_human_like(ai_output, samples)

        # Return the transformed output as JSON
        return jsonify({'generated_content': human_like_output})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)