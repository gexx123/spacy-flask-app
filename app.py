from flask import Flask, request, jsonify
import spacy
from spacy.matcher import Matcher
import requests

app = Flask(__name__)

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# Initialize the matcher
matcher = Matcher(nlp.vocab)

# Define patterns for custom entities
patterns = [
    {"label": "SUBJECT", "pattern": [{"LOWER": "mathematics"}]},
    {"label": "SUBJECT", "pattern": [{"LOWER": "science"}]},
    {"label": "SUBJECT", "pattern": [{"LOWER": "physics"}]},
    {"label": "SUBJECT", "pattern": [{"LOWER": "chemistry"}]},
    {"label": "CHAPTER", "pattern": [{"LOWER": "relations"}, {"LOWER": "and"}, {"LOWER": "functions"}]},
    {"label": "CHAPTER", "pattern": [{"LOWER": "toy"}, {"LOWER": "joy"}]},
]

# Add patterns to the matcher
for pattern in patterns:
    matcher.add(pattern["label"], [pattern["pattern"]])

def custom_ner(doc):
    matches = matcher(doc)
    spans = [spacy.tokens.Span(doc, start, end, label=nlp.vocab.strings[match_id]) for match_id, start, end in matches]
    # Filter out overlapping spans
    spans = spacy.util.filter_spans(spans)
    doc.ents = list(doc.ents) + spans
    return doc

# Add the custom NER to the pipeline
nlp.add_pipe(custom_ner, last=True)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    text = data.get('text', '')
    doc = nlp(text)
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]

    # Extract relevant fields from the entities
    subject = next((ent["text"] for ent in entities if ent["label"] == "SUBJECT"), None)
    chapter = next((ent["text"] for ent in entities if ent["label"] == "CHAPTER"), None)

    # Query the MongoDB API with the extracted fields
    params = {}
    if subject:
        params['subject'] = subject
    if chapter:
        params['chapter'] = chapter

    if params:
        response = requests.get('https://my-node-app43-2.onrender.com/api/questions', params=params)
        if response.status_code == 200:
            questions = response.json()
            return jsonify(questions)
        else:
            return jsonify({"error": "Failed to query MongoDB API"}), 500

    return jsonify(entities)

if __name__ == "__main__":
    app.run(debug=True)
