from typing import Dict, Any
from kbs.core.embeddings.base import BaseEmbedding
from kbs.core.embeddings.sentence_transformer import SentenceTransformerEmbedding
from kbs.core.embeddings.openai import OpenAIEmbedding

class EmbeddingFactory:
    """Embedding 工厂类"""
    
    @staticmethod
    def create(config: Dict[str, Any] = None) -> BaseEmbedding:
        """
        创建 Embedding 实例
        
        Args:
            embedding_type: embedding 类型，支持 "sentence_transformer" 和 "openai"
            config: 配置参数
        """
        embedding_type = config.get("type", "sentence_tansformer")
        
        if embedding_type == "sentence_transformer":
            return SentenceTransformerEmbedding(
                model_name=config.get("model_name", "all-MiniLM-L6-v2")
            )
        elif embedding_type == "openai":
            return OpenAIEmbedding(
                api_key=config.get("api_key"),
                base_url=config.get("base_url"),
                model_name=config.get("model_name", "text-embedding-3-small")
            )
        else:
            raise ValueError(f"Unsupported embedding type: {embedding_type}") 