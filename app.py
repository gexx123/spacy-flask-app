import spacy
from spacy.tokens import Span
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")

# Custom NER
def custom_ner(doc):
    matcher = nlp.matcher
    patterns = [
        {"label": "SUBJECT", "pattern": [{"LOWER": "mathematics"}]},
        {"label": "CHAPTER", "pattern": [{"LOWER": "toy"}, {"LOWER": "joy"}]},
        {"label": "CHAPTER", "pattern": [{"LOWER": "relations"}, {"LOWER": "and"}, {"LOWER": "functions"}]}
    ]
    for pattern in patterns:
        matcher.add(pattern["label"], [pattern["pattern"]])

    matches = matcher(doc)
    spans = [Span(doc, start, end, label=label) for match_id, start, end in matches]
    filtered_spans = spacy.util.filter_spans(spans)
    doc.ents = list(doc.ents) + filtered_spans
    return doc

@app.route('/analyze', methods=['POST'])
def analyze():
    text = request.json.get('text')
    doc = nlp(text)
    doc = custom_ner(doc)
    
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]

    # Assuming you have a MongoDB endpoint to get questions
    mongo_url = "https://my-node-app43-2.onrender.com/api/questions"
    try:
        response = requests.post(mongo_url, json={"entities": entities})
        response.raise_for_status()
        questions = response.json()
        return jsonify(questions)
    except requests.RequestException as e:
        return jsonify({"error": "Failed to query MongoDB API", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
