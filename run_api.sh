#!/bin/bash
source venv/bin/activate
export FLASK_APP=api.py
export FLASK_ENV=development
export FLASK_DEBUG=1
flask run --host=0.0.0.0 --port=5005 
