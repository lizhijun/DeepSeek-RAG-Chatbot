import requests
import json
import sys
import os

BASE_URL = "http://localhost:5005"

def test_documents_api():
    """测试文档列表API"""
    response = requests.get(f"{BASE_URL}/api/documents")
    if response.status_code == 200:
        print("文档列表API测试成功")
        print(f"当前文档：{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    else:
        print(f"文档列表API测试失败: {response.status_code} - {response.text}")

def test_chat_api():
    """测试通用聊天API"""
    payload = {
        "query": "什么是RAG技术?",
        "history": ""
    }
    
    response = requests.post(f"{BASE_URL}/api/chat", json=payload)
    if response.status_code == 200:
        print("聊天API测试成功")
        result = response.json()
        print(f"回答: {result.get('answer')}")
    else:
        print(f"聊天API测试失败: {response.status_code} - {response.text}")

def upload_document(file_path):
    """上传文档测试"""
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return None
    
    with open(file_path, 'rb') as file:
        files = {'file': (os.path.basename(file_path), file)}
        response = requests.post(f"{BASE_URL}/api/upload", files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"文档上传成功: {result.get('filename')}")
        print(f"文档ID: {result.get('document_id')}")
        return result.get('document_id')
    else:
        print(f"文档上传失败: {response.status_code} - {response.text}")
        return None

def test_document_chat(document_id, query):
    """测试特定文档的聊天API"""
    if not document_id:
        print("无效的文档ID")
        return
    
    payload = {
        "query": query,
        "history": ""
    }
    
    response = requests.post(f"{BASE_URL}/api/chat/{document_id}", json=payload)
    if response.status_code == 200:
        print(f"文档聊天API测试成功")
        result = response.json()
        print(f"文档: {result.get('document')}")
        print(f"回答: {result.get('answer')}")
    else:
        print(f"文档聊天API测试失败: {response.status_code} - {response.text}")

def delete_document(document_id):
    """删除文档测试"""
    if not document_id:
        print("无效的文档ID")
        return
    
    response = requests.delete(f"{BASE_URL}/api/documents/{document_id}")
    if response.status_code == 200:
        print(f"文档删除成功")
    else:
        print(f"文档删除失败: {response.status_code} - {response.text}")

if __name__ == "__main__":
    # 测试文档列表API
    test_documents_api()
    
    # 测试通用聊天API
    test_chat_api()
    
    # 如果提供了文件路径，测试文档上传和相关功能
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        document_id = upload_document(file_path)
        
        if document_id:
            # 再次测试文档列表API，确认文档已上传
            test_documents_api()
            
            # 测试特定文档的聊天API
            if len(sys.argv) > 2:
                query = sys.argv[2]
            else:
                query = "这个文档的主要内容是什么?"
                
            test_document_chat(document_id, query)
            
            # 测试删除文档
            delete_document(document_id)
            
            # 最后再次验证文档列表
            test_documents_api() 