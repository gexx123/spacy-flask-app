from flask import Flask, jsonify, request
import spacy
from spacy.tokens import Span
from spacy.language import Language
import requests
import logging

app = Flask(__name__)
<<<<<<< HEAD
logging.basicConfig(level=logging.DEBUG)

# Load Spacy model
nlp = spacy.load("en_core_web_sm")

# Define custom NER component
@Language.component("custom_ner")
def custom_ner(doc):
    matcher = spacy.matcher.Matcher(nlp.vocab)
    patterns = [
        {"label": "SUBJECT", "pattern": [{"LOWER": "mathematics"}]},
        {"label": "SUBJECT", "pattern": [{"LOWER": "physics"}]},
        {"label": "SUBJECT", "pattern": [{"LOWER": "science"}]},
        {"label": "BOOKTITLE", "pattern": [{"LOWER": "ncert"}]},
        {"label": "BOOKTITLE", "pattern": [{"LOWER": "cbse"}]},
        {"label": "BOOKTITLE", "pattern": [{"LOWER": "maths mela"}]},
        {"label": "CHAPTERNAME", "pattern": [{"LOWER": "toy joy"}]},
        {"label": "CHAPTERNAME", "pattern": [{"LOWER": "shapes"}]},
    ]
    
    for pattern in patterns:
        matcher.add(pattern["label"], [pattern["pattern"]])
    
    matches = matcher(doc)
    spans = [Span(doc, start, end, label=nlp.vocab.strings[match_id]) for match_id, start, end in matches]
    
    # Filter out overlapping spans
    filtered_spans = spacy.util.filter_spans(spans)
    non_overlapping_ents = [ent for ent in doc.ents if not any(ent.start < span.end and ent.end > span.start for span in filtered_spans)]
    doc.ents = non_overlapping_ents + filtered_spans
    return doc

# Add the custom component to the pipeline
nlp.add_pipe("custom_ner", after='ner')
=======

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

@app.route('/')
def index():
    return "Hello, World!"
>>>>>>> 018f95e9352e0bc811922310f3d8d6aa23d469ee

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    text = data.get('text', '')
    doc = nlp(text)
<<<<<<< HEAD
    entities = [{ 'text': ent.text, 'label': ent.label_ } for ent in doc.ents]
    
    # Construct the params to query MongoDB API
    params = {}
    for ent in doc.ents:
        if ent.label_ == "SUBJECT":
            params["subject"] = ent.text
        elif ent.label_ == "CHAPTERNAME":
            params["chapter"] = ent.text
        elif ent.label_ == "BOOKTITLE":
            params["booktitle"] = ent.text
    
    logging.debug(f"Querying MongoDB API with params: {params}")

    # Query MongoDB API
    try:
        response = requests.get("https://my-node-app43-2.onrender.com/api/questions", params=params)
        response.raise_for_status()
        questions = response.json()
        logging.debug(f"MongoDB API response: {questions}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error querying MongoDB API: {e}")
        return jsonify({"error": "Failed to query MongoDB API"}), 500

    return jsonify(questions)

=======
    entities = [{'text': ent.text, 'label': ent.label_} for ent in doc.ents]
    return jsonify(entities)

>>>>>>> 018f95e9352e0bc811922310f3d8d6aa23d469ee
if __name__ == "__main__":
    app.run(debug=True)
