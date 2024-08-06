import spacy
from flask import Flask, request, jsonify
import requests
from spacy.pipeline import EntityRuler
import subprocess

app = Flask(__name__)

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

# Add custom EntityRuler to the pipeline
ruler = nlp.add_pipe("entity_ruler", before="ner")

# Define patterns for custom entities
patterns = [
    {"label": "SUBJECT", "pattern": [{"LOWER": "mathematics"}]},
    {"label": "CHAPTER", "pattern": [{"LOWER": "toy"}, {"LOWER": "joy"}]},
    {"label": "CLASS", "pattern": [{"LOWER": "class"}, {"IS_DIGIT": True}]},
    {"label": "DifficultyLevel", "pattern": [{"LOWER": "easy"}]},
    {"label": "DifficultyLevel", "pattern": [{"LOWER": "medium"}]},
    {"label": "DifficultyLevel", "pattern": [{"LOWER": "hard"}]},
    {"label": "Topic", "pattern": [{"LOWER": "drawing"}]},
    {"label": "Topic", "pattern": [{"LOWER": "shape"}, {"LOWER": "identification"}]},
    {"label": "QuestionType", "pattern": [{"LOWER": "activity"}]},
    {"label": "QuestionType", "pattern": [{"LOWER": "short"}, {"LOWER": "answer"}]},
    {"label": "BookTitle", "pattern": [{"LOWER": "maths"}, {"LOWER": "mela"}]},
    {"label": "Authors", "pattern": [{"LOWER": "ncert"}]},
    # Add more patterns as needed
]

# Add patterns to the ruler
ruler.add_patterns(patterns)

def custom_ner(text):
    doc = nlp(text)
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
    return entities

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    text = data.get('text', '')
    entities = custom_ner(text)
    
    if not entities:
        return jsonify({"error": "No relevant entities found in the input text."}), 400
    
    try:
        # Update the URL to the deployed Node.js API on Render
        response = requests.post('https://my-node-app43-2.onrender.com/api/questions', json={"entities": entities})
        response.raise_for_status()
        questions_data = response.json()
        
        # Extract the question text keys' values
        question_texts = [q.get('questionText', '') for q in questions_data.get('questions', [])]
        
        return jsonify({"entities": entities, "questions": question_texts})
    except requests.RequestException as e:
        return jsonify({"error": "Failed to query MongoDB API", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
