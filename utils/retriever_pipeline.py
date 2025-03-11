import streamlit as st
from utils.build_graph import retrieve_from_graph
from langchain_core.documents import Document
import requests
import os
import json
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings

# 🚀 Query Expansion with HyDE
def expand_query(query,uri,model):
    try:
        response = requests.post(uri, json={
            "model": model,
            "prompt": f"Generate a hypothetical answer to: {query}",
            "stream": False
        }).json()
        return f"{query}\n{response.get('response', '')}"
    except Exception as e:
        if hasattr(st, 'error'):
            st.error(f"Query expansion failed: {str(e)}")
        print(f"Query expansion failed: {str(e)}")
        return query


# 🚀 Advanced Retrieval Pipeline
def retrieve_documents(query, uri, model, chat_history=""):
    expanded_query = expand_query(f"{chat_history}\n{query}", uri, model) if 'enable_hyde' in st.session_state and st.session_state.enable_hyde else query
    
    # 🔍 Retrieve documents using BM25 + FAISS
    docs = st.session_state.retrieval_pipeline["ensemble"].invoke(expanded_query)

    # 🚀 GraphRAG Retrieval
    if 'enable_graph_rag' in st.session_state and st.session_state.enable_graph_rag:
        graph_results = retrieve_from_graph(query, st.session_state.retrieval_pipeline["knowledge_graph"])
        
        # Debugging output
        if hasattr(st, 'write'):
            st.write(f"🔍 GraphRAG Retrieved Nodes: {graph_results}")

        # Ensure graph results are correctly formatted
        graph_docs = []
        for node in graph_results:
            graph_docs.append(Document(page_content=node))  # ✅ Fix: Correct Document initialization

        # If graph retrieval is successful, merge it with standard document retrieval
        if graph_docs:
            docs = graph_docs + docs  # Merge GraphRAG results with FAISS + BM25 results
    
    # 🚀 Neural Reranking (if enabled)
    if 'enable_reranking' in st.session_state and st.session_state.enable_reranking:
        pairs = [[query, doc.page_content] for doc in docs]  # ✅ Fix: Use `page_content`
        scores = st.session_state.retrieval_pipeline["reranker"].predict(pairs)

        # Sort documents based on reranking scores
        ranked_docs = [doc for _, doc in sorted(zip(scores, docs), reverse=True)]
    else:
        ranked_docs = docs

    return ranked_docs[:st.session_state.max_contexts] if 'max_contexts' in st.session_state else ranked_docs[:3]  # Return top results based on max_contexts

# 从特定文档中检索信息
def retrieve_documents_from_specific(query, document_dir, uri, model, chat_history=""):
    # 扩展查询
    expanded_query = expand_query(f"{chat_history}\n{query}", uri, model)
    
    # 加载特定文档的向量存储
    embeddings = OllamaEmbeddings(
        model_name=os.getenv("EMBEDDINGS_MODEL", "nomic-embed-text"),
        base_url=os.getenv("OLLAMA_API_URL", "http://localhost:11434")
    )
    
    # 检查向量存储文件是否存在
    vector_store_path = os.path.join(document_dir, "faiss_index")
    if not os.path.exists(vector_store_path):
        raise FileNotFoundError(f"Vector store not found for the document at {vector_store_path}")
    
    # 加载向量存储
    vector_store = FAISS.load_local(vector_store_path, embeddings)
    
    # 检索相关文档
    retrieved_docs = vector_store.similarity_search(expanded_query, k=5)
    
    return retrieved_docs
