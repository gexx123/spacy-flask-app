#!/bin/bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
gunicorn -w 4 -b 0.0.0.0:8000 app:app
