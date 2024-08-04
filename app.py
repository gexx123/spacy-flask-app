from flask import Flask, request, jsonify
import spacy
import requests

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")

MONGO_API_URL = "https://my-node-app43-2.onrender.com/api/questions"

def custom_ner(text):
    doc = nlp(text)
    spans = []
    
    # Example patterns to recognize specific entities
    for match_id, start, end in nlp.matcher(doc):
        span = doc[start:end]
        spans.append(span)

    # Filter and avoid overlapping spans
    filtered_spans = spacy.util.filter_spans(spans)
    doc.ents = list(doc.ents) + filtered_spans
    return doc

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    doc = custom_ner(text)
    entities = [{'text': ent.text, 'label': ent.label_} for ent in doc.ents]

    try:
        response = requests.post(MONGO_API_URL, json={'entities': entities})
        response.raise_for_status()
        mongo_response = response.json()
        return jsonify(mongo_response)
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Failed to query MongoDB API', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
