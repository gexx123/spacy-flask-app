import spacy
from spacy.tokens import Span
from spacy.matcher import Matcher
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)

# Add patterns to the matcher
patterns = [
    {"label": "SUBJECT", "pattern": [{"LOWER": "mathematics"}]},
    {"label": "CHAPTER", "pattern": [{"LOWER": "toy"}, {"LOWER": "joy"}]},
    {"label": "CHAPTER", "pattern": [{"LOWER": "relations"}, {"LOWER": "and"}, {"LOWER": "functions"}]}
]

for pattern in patterns:
    matcher.add(pattern["label"], [pattern["pattern"]])

def custom_ner(doc):
    matches = matcher(doc)
    spans = [Span(doc, start, end, label=nlp.vocab.strings[match_id]) for match_id, start, end in matches]
    filtered_spans = spacy.util.filter_spans(spans)

    existing_spans = {tuple(ent): ent for ent in doc.ents}
    new_spans = {tuple(span): span for span in filtered_spans if tuple(span) not in existing_spans}
    doc.ents = list(existing_spans.values()) + list(new_spans.values())
    return doc

@app.route('/analyze', methods=['POST'])
def analyze():
    text = request.json.get('text')
    doc = nlp(text)
    doc = custom_ner(doc)
    
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]

    mongo_url = "https://my-node-app43-2.onrender.com/api/questions"
    try:
        payload = {"entities": entities}
        response = requests.post(mongo_url, json=payload)
        response.raise_for_status()
        questions = response.json()
        return jsonify(questions)
    except requests.RequestException as e:
        return jsonify({"error": "Failed to query MongoDB API", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
