根据对代码的分析，我为您提供DeepSeek-RAG-Chatbot2项目的对话API信息：

## DeepSeek-RAG-Chatbot2 对话API说明

这个项目是一个基于Streamlit的RAG（检索增强生成）聊天应用，主要使用Ollama API进行大语言模型调用。以下是其API相关信息：

### 1. 主要API接口

项目主要通过Ollama API进行对话生成，核心API调用位于`app.py`文件中：

- **API端点**: 通过环境变量`OLLAMA_API_URL`设置，默认为`http://localhost:11434/api/generate`
- **调用方法**: 使用HTTP POST请求
- **API参数**:
  ```json
  {
    "model": "MODEL_NAME",
    "prompt": "YOUR_PROMPT",
    "stream": true,
    "options": {
      "temperature": TEMPERATURE_VALUE,
      "num_ctx": 4096
    }
  }
  ```

### 2. 配置设置

- **模型配置**: 在`.env`文件中设置
  - `OLLAMA_API_URL`: Ollama API的URL，默认为`http://127.0.0.1:11434`
  - `MODEL`: 使用的模型，默认为`deepseek-r1:32b`

- **Docker配置**: 在`docker-compose.yml`中设置
  - API URL: `http://host.docker.internal:11434`
  - 默认模型: `deepseek-r1:7b`
  - 嵌入模型: `nomic-embed-text:latest`
  - 重排序模型: `cross-encoder/ms-marco-MiniLM-L-6-v2`

### 3. 检索功能

在`utils/retriever_pipeline.py`中实现，主要功能：

- **查询扩展**: 使用HyDE(Hypothetical Document Embeddings)技术扩展查询
- **文档检索**: 基于向量检索(FAISS)和BM25的混合检索
- **图检索**: 可选的基于知识图谱的检索增强
- **重排序**: 使用交叉编码器进行神经网络重排序

### 4. 使用方法

1. **启动服务**:
   ```bash
   source venv/bin/activate
   streamlit run app.py
   ```

2. **Docker部署**:
   ```bash
   docker-compose up -d
   ```
   服务将在`http://localhost:8501`上可用

3. **API调用示例**:
   ```python
   import requests
   import json

   response = requests.post(
       "http://localhost:11434/api/generate",
       json={
           "model": "deepseek-r1:7b",
           "prompt": "你的问题",
           "stream": False,
           "options": {
               "temperature": 0.3,
               "num_ctx": 4096
           }
       }
   )
   result = response.json()
   print(result.get("response", ""))
   ```

### 5. 高级功能

- **HyDE**: 假设文档生成技术，增强检索效果
- **神经网络重排序**: 使用交叉编码器提高检索文档的相关性
- **图RAG**: 基于知识图谱的检索增强
- **聊天历史**: 保持对话上下文

这个项目主要是通过Streamlit提供Web UI，后端使用Ollama API实现对话生成功能，没有独立的API服务，而是通过直接调用Ollama的API来实现聊天功能。
