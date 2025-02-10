# 🚀 **DeepSeek RAG 聊天机器人 3.0 - 新增知识图谱与对话历史集成！**
**(100% 免费、隐私保护（无网络连接）、本地安装运行)**  

[![演示视频](https://img.youtube.com/vi/xDGLub5JPFE/0.jpg)](https://www.youtube.com/watch?v=xDGLub5JPFE "观看演示视频")

🔥 **DeepSeek + NOMIC + FAISS + 神经重排序 + HyDE + 知识图谱 + 对话记忆 = 终极RAG技术栈！**  

本聊天机器人支持从PDF、DOCX和TXT文件中**快速、准确、可解释地检索信息**，采用**DeepSeek-7B**、**BM25**、**FAISS**、**神经重排序（交叉编码器）**、**知识图谱**和**对话历史集成**技术。

---

## **🔹 新版特性**

- **知识图谱集成：** 从文档构建**知识图谱**，实现更**上下文相关**的语义理解  
- **对话历史记忆功能：** 通过引用**对话历史**保持上下文，生成更**连贯**且**相关**的回复  
- **改进的错误处理：** 修复了**对话历史清除**相关问题及其他小问题，提供**更流畅的体验**  

---

# **安装与配置**

可通过以下两种方式安装运行**DeepSeek RAG聊天机器人**：

1. **传统Python虚拟环境安装**  
2. **Docker容器化部署**（推荐生产环境使用）

---

## **1️⃣ 传统Python虚拟环境安装**

### **步骤A：克隆仓库并安装依赖**
```bash
git clone https://github.com/SaiAkhil066/DeepSeek-RAG-Chatbot.git
cd DeepSeek-RAG-Chatbot

# 创建虚拟环境
python -m venv venv

# 激活环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 升级pip（推荐）
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt
```

### **步骤B：下载并配置Ollama**
1. **下载Ollama** → [https://ollama.com/](https://ollama.com/)  
2. **拉取所需模型**：
   ```bash
   ollama pull deepseek-r1:7b
   ollama pull nomic-embed-text
   ```
   *注：如需使用其他模型，请更新环境变量或`.env`文件中的`MODEL`和`EMBEDDINGS_MODEL`参数*

### **步骤C：运行聊天机器人**
1. 确保**Ollama**服务已启动：
   ```bash
   ollama serve
   ```
2. 启动Streamlit应用：
   ```bash
   streamlit run app.py
   ```
3. 在浏览器访问 **[http://localhost:8501](http://localhost:8501)** 使用聊天界面

---

## **2️⃣ Docker安装**

### **A) 单容器方案（主机运行Ollama）**

如果**Ollama**已安装在**宿主机**并监听`localhost:11434`：

1. **构建并运行**：
   ```bash
   docker-compose build
   docker-compose up
   ```
2. 应用将运行于 **[http://localhost:8501](http://localhost:8501)**，容器通过指定URL访问宿主机Ollama服务

### **B) 双容器方案（Docker运行Ollama）**
```yaml
version: "3.8"

services:
  ollama:
    image: ghcr.io/jmorganca/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"

  deepgraph-rag-service:
    container_name: deepgraph-rag-service
    build: .
    ports:
      - "8501:8501"
    environment:
      - OLLAMA_API_URL=http://ollama:11434
      - MODEL=deepseek-r1:7b
      - EMBEDDINGS_MODEL=nomic-embed-text:latest
      - CROSS_ENCODER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2
    depends_on:
      - ollama
```

运行：
```bash
docker-compose build
docker-compose up
```
Ollama和聊天机器人均运行在Docker中，访问 **[http://localhost:8501](http://localhost:8501)** 使用

---

# **工作原理**

1. **文档上传**：通过侧边栏上传PDF/DOCX/TXT文件  
2. **混合检索**：结合**BM25**和**FAISS**获取最相关文本片段  
3. **知识图谱处理**：从文档构建**知识图谱**理解实体关系  
4. **神经重排序**：使用**交叉编码器**模型对结果进行相关性重排序  
5. **查询扩展（HyDE）**：生成假设答案扩展查询范围  
6. **对话历史集成**：参考历史对话保持上下文连贯  
7. **DeepSeek-7B生成**：基于最优片段生成最终回答

---

## **🔹 版本升级亮点**

| 功能                      | 旧版                         | 新版                          |
|--------------------------|-----------------------------|-------------------------------|
| **检索方式**            | 混合检索（BM25 + FAISS）   | 混合检索 + **知识图谱**       |
| **上下文理解**          | 有限                        | **基于知识图谱的增强理解**    |
| **用户界面**            | 标准                        | **可定制主题侧边栏**          |
| **对话历史**            | 未使用                      | **完整记忆集成**              |
| **错误处理**            | 基础                        | **改进的错误修复机制**        |

---

## **📌 参与贡献**

- **Fork** 本仓库，提交**Pull Request**或创建**Issue**建议新功能/修复问题  
- 欢迎提出改进建议，共同完善聊天机器人

---

### **🔗 联系我们**

欢迎在[**Reddit**](https://www.reddit.com/user/akhilpanja/)分享您的使用体验和建议！🚀💡

---

**立即体验知识图谱构建、对话记忆管理和本地LLM的强大能力——完全在您的设备上运行！**  
_检索增强型AI的未来已来——无需网络连接！_
