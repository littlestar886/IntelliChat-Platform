import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import docx
from docx import Document
import re

def create_rag_retriever(docx_path: str, model_name: str = "BAAI/bge-small-zh-v1.5", similarity_threshold: float = 0.5) -> callable:
    """
    创建一个基于 RAG (检索增强生成) 的问答检索器函数
    
    参数:
    - docx_path: 包含知识库的 DOCX 文件路径
    - model_name: 用于文本嵌入的模型名称，默认为 BAAI/bge-small-zh-v1.5
    - similarity_threshold: 检索结果的相似度阈值，低于此值返回默认提示
    
    返回:
    - 一个可调用的检索函数，接受问题字符串并返回相关答案
    """
    # 设置环境变量
    os.environ['KERAS_BACKEND'] = 'tensorflow'
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
    os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
    
    def split_into_sentences(text: str) -> List[str]:
        """将文本分割成句子"""
        sentences = re.split(r'(?<=[。！？])', text)
        return [s.strip() for s in sentences if s.strip()]
    
    try:
        # 读取文档内容
        doc = Document(docx_path)
        documents = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
        
        if not documents:
            raise ValueError("文档内容为空")
            
        # 初始化模型
        model = SentenceTransformer(model_name)
        dim = model.get_sentence_embedding_dimension()
        
        # 构建索引
        sentences = []
        for para in documents:
            sentences.extend(split_into_sentences(para))
            
        embeddings = model.encode(sentences, normalize_embeddings=True)
        index = faiss.IndexFlatIP(dim)
        index.add(embeddings.astype(np.float32))
        
        def retrieve(question: str, top_k: int = 1) -> str:
            """执行检索，返回最相关的内容"""
            query_embedding = model.encode(question, normalize_embeddings=True)
            scores, indices = index.search(np.array([query_embedding]), top_k)
            
            if scores[0][0] > similarity_threshold:
                return sentences[indices[0][0]]
            return "未找到相关答案"
            
        return retrieve
        
    except Exception as e:
        print(f"初始化检索器失败: {str(e)}")
        return lambda _: "检索器初始化失败，请检查文档路径和格式"
