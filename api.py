# 创建一个新文件 api.py
from flask import Flask, request, jsonify
from utils.retriever_pipeline import retrieve_documents, expand_query, retrieve_documents_from_specific
from utils.doc_handler import process_documents, process_document_bytes
import requests
import os
import uuid
import json
from werkzeug.utils import secure_filename
import tempfile
from flask_cors import CORS
from dotenv import load_dotenv
import datetime

# 加载环境变量
load_dotenv()

# 设置默认值
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
MODEL = os.getenv("MODEL", "deepseek-r1:7b")
EMBEDDINGS_MODEL = os.getenv("EMBEDDINGS_MODEL", "nomic-embed-text:latest")
CROSS_ENCODER_MODEL = os.getenv("CROSS_ENCODER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")

app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 创建临时目录用于存储上传的文档和处理结果
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 文档ID到文档路径的映射
documents_registry = {}
if os.path.exists(os.path.join(UPLOAD_FOLDER, "documents_registry.json")):
    with open(os.path.join(UPLOAD_FOLDER, "documents_registry.json"), "r") as f:
        documents_registry = json.load(f)

# 保存文档注册表
def save_registry():
    with open(os.path.join(UPLOAD_FOLDER, "documents_registry.json"), "w") as f:
        json.dump(documents_registry, f)

# 基本聊天API，使用全局知识库
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    query = data.get('query')
    chat_history = data.get('history', '')
    
    # 直接构建响应
    system_prompt = f"""Based on your knowledge, please answer this question:
        Question: {query}
        Answer:"""
    
    # 调用Ollama API
    try:
        response = requests.post(
            f"{OLLAMA_API_URL}/api/generate",
            json={
                "model": MODEL,
                "prompt": system_prompt,
                "options": {
                    "temperature": 0.3,
                    "num_ctx": 4096
                }
            }
        ).json()
        
        return jsonify({
            "answer": response.get("response", ""),
            "sources": []
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 文档上传API
@app.route('/api/upload', methods=['POST'])
def upload_document():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # 检查文件类型
    allowed_extensions = {'pdf', 'docx', 'txt'}
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({"error": f"File type not allowed. Supported types: {', '.join(allowed_extensions)}"}), 400
    
    # 生成唯一文档ID
    document_id = str(uuid.uuid4())
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, f"{document_id}_{filename}")
    
    # 保存文件
    file.save(file_path)
    
    try:
        # 处理文档
        with tempfile.TemporaryDirectory() as temp_dir:
            # 处理文档并创建向量存储
            process_document_bytes(file.read(), file.filename, temp_dir,
                                  EMBEDDINGS_MODEL, OLLAMA_API_URL)
            
            # 移动处理结果到正式目录
            result_dir = os.path.join(UPLOAD_FOLDER, document_id)
            os.makedirs(result_dir, exist_ok=True)
            
            # 记录文档信息
            documents_registry[document_id] = {
                "filename": filename,
                "path": file_path,
                "result_dir": result_dir,
                "upload_time": str(datetime.datetime.now())
            }
            save_registry()
            
            return jsonify({
                "document_id": document_id,
                "filename": filename,
                "message": "Document uploaded and processed successfully"
            })
    except Exception as e:
        # 删除文件
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({"error": str(e)}), 500

# 特定文档问答API
@app.route('/api/chat/<document_id>', methods=['POST'])
def chat_with_document(document_id):
    if document_id not in documents_registry:
        return jsonify({"error": "Document not found"}), 404
    
    data = request.json
    query = data.get('query')
    chat_history = data.get('history', '')
    
    # 从特定文档检索
    try:
        # 使用特定文档的向量存储路径
        docs = retrieve_documents_from_specific(
            query, 
            documents_registry[document_id]["result_dir"],
            f"{OLLAMA_API_URL}/api/generate", 
            MODEL, 
            chat_history
        )
        
        context = "\n".join([f"[Source {i+1}]: {doc.page_content}" 
                            for i, doc in enumerate(docs)])
        
        # 构建系统提示
        system_prompt = f"""Use the chat history to maintain context:
            Chat History:
            {chat_history}
            
            Context from document '{documents_registry[document_id]["filename"]}':
            {context}
            
            Question: {query}
            Answer:"""
        
        # 调用Ollama API
        response = requests.post(
            f"{OLLAMA_API_URL}/api/generate",
            json={
                "model": MODEL,
                "prompt": system_prompt,
                "options": {
                    "temperature": 0.3,
                    "num_ctx": 4096
                }
            }
        ).json()
        
        return jsonify({
            "answer": response.get("response", ""),
            "sources": [doc.page_content for doc in docs],
            "document": documents_registry[document_id]["filename"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 获取所有文档列表
@app.route('/api/documents', methods=['GET'])
def list_documents():
    documents = []
    for doc_id, doc_info in documents_registry.items():
        documents.append({
            "document_id": doc_id,
            "filename": doc_info["filename"],
            "upload_time": doc_info["upload_time"]
        })
    return jsonify({"documents": documents})

# 删除文档
@app.route('/api/documents/<document_id>', methods=['DELETE'])
def delete_document(document_id):
    if document_id not in documents_registry:
        return jsonify({"error": "Document not found"}), 404
    
    try:
        # 删除文件和结果目录
        if os.path.exists(documents_registry[document_id]["path"]):
            os.remove(documents_registry[document_id]["path"])
        
        if os.path.exists(documents_registry[document_id]["result_dir"]):
            import shutil
            shutil.rmtree(documents_registry[document_id]["result_dir"])
        
        # 从注册表中删除
        del documents_registry[document_id]
        save_registry()
        
        return jsonify({"message": "Document deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
