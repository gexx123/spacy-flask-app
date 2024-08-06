import spacy
from flask import Flask, request, jsonify
import requests
import subprocess
import openai
import os

app = Flask(__name__)

# Set the OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

# Ensure the OpenAI API key is set
if not openai.api_key:
    raise ValueError("No OpenAI API key provided. Please set the OPENAI_API_KEY environment variable.")

# Function to download and link the spaCy model
def download_spacy_model(model_name):
    try:
        subprocess.run(["python", "-m", "spacy", "download", model_name], check=True)
        subprocess.run(["python", "-m", "spacy", "link", model_name, model_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to download or link spaCy model: {e}")
        raise

# Ensure the correct model name is used
model_name = "en_core_web_sm"

# Check if the model is already installed, if not download and link it
try:
    nlp = spacy.load(model_name)
except OSError:
    download_spacy_model(model_name)
    nlp = spacy.load(model_name)

def generate_response(prompt):
    try:
        response = openai.Completion.create(
            engine="gpt-4",
            prompt=prompt,
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Error generating response: {e}")
        return "Error generating response"

def custom_ner(text):
    try:
        response = openai.Completion.create(
            engine="gpt-4",
            prompt=f"Extract entities and their types from the following text: {text}",
            max_tokens=150
        )
        entities_text = response.choices[0].text.strip()
        entities = []
        for line in entities_text.split('\n'):
            if ':' in line:
                label, entity = line.split(':', 1)
                entities.append({"label": label.strip(), "text": entity.strip()})
        return entities
    except Exception as e:
        print(f"Error extracting entities: {e}")
        return []

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    text = data.get('text', '')
    entities = custom_ner(text)
    ai_response = generate_response(text)
    
    try:
        # Update the URL to the deployed Node.js API on Render
        response = requests.post('https://my-node-app43-2.onrender.com/api/questions', json={"entities": entities})
        response.raise_for_status()
        questions_data = response.json()
        
        # Extract the question text keys' values
        question_texts = [q.get('questionText', '') for q in questions_data.get('questions', [])]
        
        return jsonify({"entities": entities, "questions": question_texts, "ai_response": ai_response})
    except requests.RequestException as e:
        print(f"RequestException: {e}")
        return jsonify({"error": "Failed to query MongoDB API", "details": str(e)}), 500
    except Exception as e:
        print(f"Exception: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
