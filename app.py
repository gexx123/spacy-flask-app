import spacy
from flask import Flask, request, jsonify
import requests
from spacy.pipeline import EntityRuler
import subprocess
from textblob import TextBlob
import openai
import os
import logging

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

# Function to download and link the spaCy model
def download_spacy_model(model_name):
    try:
        subprocess.run(["python", "-m", "spacy", "download", model_name], check=True)
        subprocess.run(["python", "-m", "spacy", "link", model_name, model_name], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to download or link spaCy model: {e}")
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

# Function to analyze sentiment
def analyze_sentiment(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity

# Function to generate response using GPT-3
def generate_response(prompt):
    response = openai.Completion.create(
      engine="davinci",
      prompt=prompt,
      max_tokens=50
    )
    return response.choices[0].text.strip()

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    text = data.get('text', '')
    logger.info(f"Received text: {text}")
    entities = custom_ner(text)
    logger.info(f"Extracted entities: {entities}")
    sentiment = analyze_sentiment(text)
    logger.info(f"Analyzed sentiment: {sentiment}")
    ai_response = generate_response(text)
    logger.info(f"Generated AI response: {ai_response}")
    
    if not entities:
        return jsonify({"error": "No relevant entities found in the input text."}), 400
    
    try:
        # Update the URL to the deployed Node.js API on Render
        response = requests.post('https://my-node-app43-2.onrender.com/api/questions', json={"entities": entities})
        response.raise_for_status()
        questions_data = response.json()
        logger.info(f"Received questions data: {questions_data}")
        
        # Extract the question text keys' values
        question_texts = [q.get('questionText', '') for q in questions_data.get('questions', [])]
        
        return jsonify({
            "entities": entities,
            "questions": question_texts,
            "sentiment": sentiment,
            "ai_response": ai_response
        })
    except requests.RequestException as e:
        logger.error(f"Failed to query MongoDB API: {e}")
        return jsonify({"error": "Failed to query MongoDB API", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"Internal Server Error: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
