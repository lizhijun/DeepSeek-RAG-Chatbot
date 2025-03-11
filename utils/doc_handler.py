import streamlit as st
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from utils.build_graph import build_knowledge_graph
from rank_bm25 import BM25Okapi
import os
import re
import tempfile
import shutil
from sentence_transformers import CrossEncoder
import torch
from pathlib import Path


def process_documents(uploaded_files,reranker,embedding_model, base_url):
    if st.session_state.documents_loaded:
        return

    st.session_state.processing = True
    documents = []
    
    # Create temp directory
    if not os.path.exists("temp"):
        os.makedirs("temp")
    
    # Process files
    for file in uploaded_files:
        try:
            file_path = os.path.join("temp", file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())

            if file.name.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
            elif file.name.endswith(".docx"):
                loader = Docx2txtLoader(file_path)
            elif file.name.endswith(".txt"):
                loader = TextLoader(file_path)
            else:
                continue
                
            documents.extend(loader.load())
            os.remove(file_path)
        except Exception as e:
            st.error(f"Error processing {file.name}: {str(e)}")
            return

    # Text splitting
    text_splitter = CharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separator="\n"
    )
    texts = text_splitter.split_documents(documents)
    text_contents = [doc.page_content for doc in texts]

    # 🚀 Hybrid Retrieval Setup
    embeddings = OllamaEmbeddings(model=embedding_model, base_url=base_url)
    
    # Vector store
    vector_store = FAISS.from_documents(texts, embeddings)
    
    # BM25 store
    bm25_retriever = BM25Retriever.from_texts(
        text_contents, 
        bm25_impl=BM25Okapi,
        preprocess_func=lambda text: re.sub(r"\W+", " ", text).lower().split()
    )

    # Ensemble retrieval
    ensemble_retriever = EnsembleRetriever(
        retrievers=[
            bm25_retriever,
            vector_store.as_retriever(search_kwargs={"k": 5})
        ],
        weights=[0.4, 0.6]
    )

    # Store in session
    st.session_state.retrieval_pipeline = {
        "ensemble": ensemble_retriever,
        "reranker": reranker,  # Now using the global reranker variable
        "texts": text_contents,
        "knowledge_graph": build_knowledge_graph(texts)  # Store Knowledge Graph
    }

    st.session_state.documents_loaded = True
    st.session_state.processing = False

    # ✅ Debugging: Print Knowledge Graph Nodes & Edges
    if "knowledge_graph" in st.session_state.retrieval_pipeline:
        G = st.session_state.retrieval_pipeline["knowledge_graph"]
        st.write(f"🔗 Total Nodes: {len(G.nodes)}")
        st.write(f"🔗 Total Edges: {len(G.edges)}")
        st.write(f"🔗 Sample Nodes: {list(G.nodes)[:10]}")
        st.write(f"🔗 Sample Edges: {list(G.edges)[:10]}")

# 处理文档字节流，用于API上传
def process_document_bytes(file_bytes, filename, output_dir, embedding_model="nomic-embed-text", base_url="http://localhost:11434"):
    """
    处理从API上传的文档字节流
    
    Args:
        file_bytes: 文件的字节内容
        filename: 文件名
        output_dir: 输出目录
        embedding_model: 嵌入模型名称
        base_url: Ollama API基础URL
    
    Returns:
        向量存储路径和知识图谱
    """
    # 创建临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as temp_file:
        temp_file.write(file_bytes)
        temp_file_path = temp_file.name
    
    try:
        # 根据文件类型选择加载器
        if filename.lower().endswith('.pdf'):
            loader = PyPDFLoader(temp_file_path)
        elif filename.lower().endswith('.docx'):
            loader = Docx2txtLoader(temp_file_path)
        elif filename.lower().endswith('.txt'):
            loader = TextLoader(temp_file_path)
        else:
            raise ValueError(f"Unsupported file type: {filename}")
        
        # 加载文档
        documents = loader.load()
        
        # 文本分割
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        docs = text_splitter.split_documents(documents)
        
        # 创建向量存储
        embeddings = OllamaEmbeddings(
            model_name=embedding_model,
            base_url=base_url
        )
        
        # 创建BM25检索器
        corpus = [doc.page_content for doc in docs]
        bm25 = BM25Okapi(corpus)
        bm25_retriever = BM25Retriever.from_texts(corpus, docs)
        
        # 创建FAISS向量存储
        vectorstore = FAISS.from_documents(docs, embeddings)
        
        # 存储向量索引
        faiss_path = os.path.join(output_dir, "faiss_index")
        vectorstore.save_local(faiss_path)
        
        # 构建知识图谱（可选）
        knowledge_graph = build_knowledge_graph(docs)
        
        # 创建检索管道结果
        retrieval_pipeline = {
            "faiss": vectorstore.as_retriever(search_kwargs={"k": 3}),
            "bm25": bm25_retriever,
            "ensemble": EnsembleRetriever(
                retrievers=[
                    vectorstore.as_retriever(search_kwargs={"k": 3}),
                    bm25_retriever
                ],
                weights=[0.5, 0.5]
            ),
            "knowledge_graph": knowledge_graph
        }
        
        # 尝试加载重排序模型
        device = "cuda" if torch.cuda.is_available() else "cpu"
        try:
            reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", device=device)
            retrieval_pipeline["reranker"] = reranker
        except Exception as e:
            print(f"Failed to load CrossEncoder model: {str(e)}")
        
        # 保存检索管道（可选）
        # 此处可以添加序列化保存检索管道的代码
        
        return retrieval_pipeline
    
    finally:
        # 删除临时文件
        os.unlink(temp_file_path)
