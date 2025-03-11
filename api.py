# 创建一个新文件 api.py
from flask import Flask, request, jsonify
from utils.retriever_pipeline import retrieve_documents
import requests
import os

app = Flask(__name__)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    query = data.get('query')
    chat_history = data.get('history', '')
    
    # 使用现有的检索管道
    docs = retrieve_documents(query, os.getenv("OLLAMA_API_URL") + "/api/generate", 
                            os.getenv("MODEL"), chat_history)
    
    context = "\n".join([f"[Source {i+1}]: {doc.page_content}" 
                        for i, doc in enumerate(docs)])
    
    # 构建系统提示
    system_prompt = f"""Use the chat history to maintain context:
        Chat History:
        {chat_history}
        
        Context:
        {context}
        
        Question: {query}
        Answer:"""
    
    # 调用Ollama API
    response = requests.post(
        os.getenv("OLLAMA_API_URL") + "/api/generate",
        json={
            "model": os.getenv("MODEL"),
            "prompt": system_prompt,
            "options": {
                "temperature": 0.3,
                "num_ctx": 4096
            }
        }
    ).json()
    
    return jsonify({
        "answer": response.get("response", ""),
        "sources": [doc.page_content for doc in docs]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
