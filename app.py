import spacy
from flask import Flask, request, jsonify
import requests
from spacy.pipeline import EntityRuler

app = Flask(__name__)

nlp = spacy.load("en_core_web_sm")

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

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    text = data.get('text', '')
    entities = custom_ner(text)
    try:
        # Update the URL to the deployed Node.js API on Render
        response = requests.post('https://my-node-app43-2.onrender.com/api/questions', json={"entities": entities})
        response.raise_for_status()
        questions_data = response.json()
        
        # Extract the question text keys' values
        question_texts = [q.get('questionText', '') for q in questions_data.get('questions', [])]
        
        return jsonify({"entities": entities, "questions": question_texts})
    except requests.RequestException as e:
        return jsonify({"error": "Failed to query MongoDB API", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
