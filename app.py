import spacy
from flask import Flask, request, jsonify
import requests
import subprocess
import sys

app = Flask(__name__)

# Function to download and load the spaCy model
def load_model(model_name):
    try:
        nlp = spacy.load(model_name)
    except OSError:
        # If the model is not found, download it
        subprocess.run([sys.executable, "-m", "spacy", "download", model_name])
        nlp = spacy.load(model_name)
    return nlp

# Load the spaCy model
nlp = load_model("en_core_web_sm")

# Function to perform custom Named Entity Recognition
def custom_ner(doc):
    matcher = spacy.matcher.Matcher(nlp.vocab)

    patterns = [
        {"label": "SUBJECT", "pattern": [{"LOWER": "mathematics"}]},
        {"label": "CHAPTER", "pattern": [{"LOWER": "relations"}, {"LOWER": "and"}, {"LOWER": "functions"}]}
    ]

    for pattern in patterns:
        matcher.add(pattern["label"], [pattern["pattern"]])

    matches = matcher(doc)
    spans = [spacy.tokens.Span(doc, start, end, label=nlp.vocab.strings[match_id]) for match_id, start, end in matches]
    
    # Filter out overlapping spans
    filtered_spans = spacy.util.filter_spans(spans)
    
    # Ensure no overlapping spans
    existing_entities = list(doc.ents)
    non_overlapping_spans = [span for span in filtered_spans if not any(span.start < ent.end and span.end > ent.start for ent in existing_entities)]
    doc.ents = existing_entities + non_overlapping_spans
    return doc

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    text = data.get('text', '')

    doc = nlp(text)
    doc = custom_ner(doc)
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]

    # MongoDB API URL
    mongo_api_url = "https://my-node-app43-2.onrender.com/api/questions"

    # Mapping of labels to MongoDB query fields
    label_to_field = {
        "CHAPTER": "chapter",
        "DIFFICULTYLEVEL": "DifficultyLevel",
        "SUBJECT": "Subject",
        "TOPIC": "Topic",
        "QUESTIONTYPE": "QuestionType",
        "BOOKTITLE": "BookTitle",
        "AUTHORS": "Authors"
    }

    query_params = {}
    for entity in entities:
        field = label_to_field.get(entity["label"])
        if field:
            query_params[field] = entity["text"]

    try:
        response = requests.get(mongo_api_url, params=query_params)
        response.raise_for_status()
        questions = response.json()
    except requests.RequestException:
        return jsonify({"error": "Failed to query MongoDB API"}), 500

    return jsonify(questions)

if __name__ == "__main__":
    app.run(debug=True)
