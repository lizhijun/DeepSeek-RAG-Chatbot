from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

OLLAMA_API_URL = "http://localhost:11434"
MODEL = "deepseek-r1:7b"

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    query = data.get('query', 'Hello')
    
    try:
        response = requests.post(
            f"{OLLAMA_API_URL}/api/generate",
            json={
                "model": MODEL,
                "prompt": f"Question: {query}\nAnswer:",
                "options": {
                    "temperature": 0.3
                }
            }
        ).json()
        
        return jsonify({
            "answer": response.get("response", ""),
            "sources": []
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"status": "ok", "message": "API is working"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True) 