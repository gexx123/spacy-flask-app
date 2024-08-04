from flask import Flask, request, jsonify
import spacy
import requests

app = Flask(__name__)

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# MongoDB API URL
mongo_url = "https://my-node-app43-2.onrender.com/api/questions"

# Custom NER function
def custom_ner(text):
    doc = nlp(text)
    matcher = spacy.matcher.Matcher(nlp.vocab)
    
    patterns = [
        [{"LOWER": "question"}, {"LOWER": "paper"}],
        [{"LOWER": "chapter"}]
    ]
    matcher.add("QUESTION_PAPER", [patterns[0]])
    matcher.add("CHAPTER", [patterns[1]])
    
    matches = matcher(doc)
    
    spans = []
    for match_id, start, end in matches:
        span = doc[start:end]
        label = nlp.vocab.strings[match_id]
        spans.append((label, span))
    
    entities = []
    for label, span in spans:
        entities.append({"text": span.text, "label": label})
    
    return entities

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    entities = custom_ner(text)
    
    # Make a POST request to the MongoDB API
    try:
        response = requests.post(mongo_url, json={"entities": entities})
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to query MongoDB API", "details": str(e)}), 500
    
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True)
