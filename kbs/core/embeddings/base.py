from abc import ABC, abstractmethod
from typing import List

class BaseEmbedding(ABC):
    """Embedding 基类"""
    
    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """将查询文本转换为向量"""
        pass
        
    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """将文档文本列表转换为向量列表"""
        pass 