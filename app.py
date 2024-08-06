import spacy
from flask import Flask, request, jsonify
import requests
from spacy.pipeline import EntityRuler
import subprocess
from textblob import TextBlob
import openai
import logging
import os

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Set OpenAI API key directly from environment variables
api_key = os.getenv('OPENAI_API_KEY', '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')

if not api_key:
    logger.error("OpenAI API key not found. Please set it in the environment variables.")
else:
    openai.api_key = api_key

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
    {"label": "SUBJECT", "pattern": "Mathematics"},
    {"label": "CHAPTER", "pattern": "Toy Joy"},
    {"label": "CLASS", "pattern": "Class 10"},
    {"label": "DifficultyLevel", "pattern": "Easy"},
    {"label": "DifficultyLevel", "pattern": "Medium"},
    {"label": "DifficultyLevel", "pattern": "Hard"},
    {"label": "Topic", "pattern": "Drawing"},
    {"label": "Topic", "pattern": "Shape Identification"},
    {"label": "QuestionType", "pattern": "Activity"},
    {"label": "QuestionType", "pattern": "Short Answer"},
    {"label": "BookTitle", "pattern": "Maths Mela"},
    {"label": "Authors", "pattern": "NCERT"},
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

# Function to generate response using OpenAI GPT-3
def generate_response(prompt):
    try:
        logger.debug(f"Generating response for prompt: {prompt}")
        response = openai.Completion.create(
            engine="davinci",
            prompt=prompt,
            max_tokens=50
        )
        logger.debug(f"OpenAI response: {response}")
        return response.choices[0].text.strip()
    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI error: {e}")
        return "Error generating response"
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return "Error generating response"

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        if not data or 'text' not in data:
            logger.error("Invalid request: no text provided")
            return jsonify({"error": "Invalid request: no text provided"}), 400
        
        text = data['text']
        logger.debug(f"Analyzing text: {text}")
        
        entities = custom_ner(text)
        logger.debug(f"Extracted entities: {entities}")
        
        sentiment = analyze_sentiment(text)
        logger.debug(f"Analyzed sentiment: {sentiment}")
        
        ai_response = generate_response(text)
        logger.debug(f"Generated AI response: {ai_response}")

        response = requests.post('https://my-node-app43-2.onrender.com/api/questions', json={"entities": entities})
        response.raise_for_status()
        questions_data = response.json()
        logger.debug(f"Received questions data: {questions_data}")
        
        question_texts = [q.get('questionText', '') for q in questions_data.get('questions', [])]
        
        return jsonify({"entities": entities, "questions": question_texts, "sentiment": sentiment, "ai_response": ai_response})
    except requests.RequestException as e:
        logger.error(f"Failed to query MongoDB API: {e}")
        return jsonify({"error": "Failed to query MongoDB API", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"Internal Server Error: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
