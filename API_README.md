# DeepSeek RAG API 服务

这是DeepSeek RAG聊天机器人的API服务部署指南，提供文档上传和知识库问答功能。

## 功能特点

- **文档上传**: 支持PDF、DOCX和TXT格式文档的上传和处理
- **特定文档问答**: 针对特定上传文档进行问答
- **通用知识库问答**: 使用全局知识库进行问答
- **文档管理**: 查看、删除已上传的文档

## 部署指南

### 前提条件

1. Python 3.8+
2. Ollama服务已运行 (`ollama serve`)
3. 已安装所需模型:
   ```bash
   ollama pull deepseek-r1:7b
   ollama pull nomic-embed-text
   ```

### 安装步骤

1. **克隆仓库并进入目录**
   ```bash
   git clone https://github.com/yourusername/DeepSeek-RAG-Chatbot2.git
   cd DeepSeek-RAG-Chatbot2
   ```

2. **创建并激活虚拟环境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate  # Windows
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **初始化必要目录**
   ```bash
   ./create_dirs.sh
   ```

5. **配置环境变量**

   创建或编辑`.env`文件:
   ```
   OLLAMA_API_URL=http://127.0.0.1:11434
   MODEL=deepseek-r1:7b
   EMBEDDINGS_MODEL=nomic-embed-text:latest
   CROSS_ENCODER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2
   ```

### 运行服务

#### 开发环境
```bash
./run_api.sh
```

#### 生产环境
```bash
./run_production.sh
```

服务将在`http://your-server-ip:5005`上运行。

## API使用指南

### 1. 上传文档

**请求**:
```bash
curl -X POST http://your-server-ip:5005/api/upload \
  -F "file=@/path/to/your/document.pdf"
```

**响应**:
```json
{
  "document_id": "8f7d1c3e-1a2b-3c4d-5e6f-7g8h9i0j1k2l",
  "filename": "document.pdf",
  "message": "Document uploaded and processed successfully"
}
```

### 2. 获取文档列表

**请求**:
```bash
curl -X GET http://your-server-ip:5005/api/documents
```

**响应**:
```json
{
  "documents": [
    {
      "document_id": "8f7d1c3e-1a2b-3c4d-5e6f-7g8h9i0j1k2l",
      "filename": "document.pdf",
      "upload_time": "2023-04-01 14:30:45.123456"
    }
  ]
}
```

### 3. 删除文档

**请求**:
```bash
curl -X DELETE http://your-server-ip:5005/api/documents/8f7d1c3e-1a2b-3c4d-5e6f-7g8h9i0j1k2l
```

**响应**:
```json
{
  "message": "Document deleted successfully"
}
```

### 4. 与特定文档进行问答

**请求**:
```bash
curl -X POST http://your-server-ip:5005/api/chat/8f7d1c3e-1a2b-3c4d-5e6f-7g8h9i0j1k2l \
  -H "Content-Type: application/json" \
  -d '{
    "query": "文档中关于X的内容是什么?",
    "history": "可选的聊天历史"
  }'
```

**响应**:
```json
{
  "answer": "根据文档，关于X的内容是...",
  "sources": ["文档中的相关片段1", "文档中的相关片段2"],
  "document": "document.pdf"
}
```

### 5. 使用全局知识库问答

**请求**:
```bash
curl -X POST http://your-server-ip:5005/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "什么是RAG技术?",
    "history": "可选的聊天历史"
  }'
```

**响应**:
```json
{
  "answer": "RAG (检索增强生成) 是一种技术...",
  "sources": ["来源1", "来源2"]
}
```

## 生产环境部署建议

1. **使用反向代理**:
   使用Nginx或Apache作为反向代理，配置SSL证书实现HTTPS访问。

2. **进程监控**:
   使用Supervisor或Systemd管理进程，确保服务持续运行。

3. **负载均衡**:
   在高并发环境下，考虑使用负载均衡器分发请求。

4. **日志管理**:
   配置日志轮转以避免日志文件过大。

5. **定期备份**:
   定期备份上传的文档和向量数据库。

## 故障排除

1. **服务启动失败**:
   - 检查Ollama服务是否运行
   - 检查环境变量是否正确设置
   - 查看错误日志 (`logs/error.log`)

2. **文档处理失败**:
   - 确保文档格式正确
   - 检查是否有足够的存储空间
   - 确认Ollama embeddings模型已正确安装

3. **API返回50x错误**:
   - 查看错误日志了解具体错误原因
   - 可能是内存不足或处理超时，考虑增加资源或调整超时设置

## 安全注意事项

1. API服务默认不包含身份验证，在生产环境中应添加适当的身份验证机制
2. 考虑限制上传文件大小以防止滥用
3. 实施速率限制以防止API被滥用

## 许可证

请参阅LICENSE文件了解详情。 