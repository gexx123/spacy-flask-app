from flask import Flask, jsonify, request
import spacy

app = Flask(__name__)

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    text = data.get('text', '')
    doc = nlp(text)
    entities = [{'text': ent.text, 'label': ent.label_} for ent in doc.ents]
    return jsonify(entities)

if __name__ == "__main__":
    app.run(debug=True)
