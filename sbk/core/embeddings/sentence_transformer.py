from typing import List
from sentence_transformers import SentenceTransformer as ST
from .base import BaseEmbedding

class SentenceTransformerEmbedding(BaseEmbedding):
    """基于 SentenceTransformer 的 Embedding 实现"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = ST(model_name)
        
    def embed_query(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()
        
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts).tolist() 