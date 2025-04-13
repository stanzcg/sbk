from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from kbs.core.database import Base

class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    vector_store_path = Column(String(255), nullable=False)  # 向量库存储路径
    document_store_path = Column(String(255), nullable=False)  # 文档存储路径
    config = Column(JSON, nullable=False, default={})  # 存储embedding配置
    status = Column(String(50), nullable=False, default="active")  # 知识库状态：active, inactive, processing
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def embedding_config(self):
        return self.config.get("embedding", {
            "type": "sentence_transformer",
            "model_name": "all-MiniLM-L6-v2"
        })

    @property
    def retrieval_config(self):
        return self.config.get("retrieval", {
            "type": "hybrid",  # hybrid, vector, bm25
            "vector_weight": 0.7,
            "bm25_weight": 0.3
        })

    @property
    def api_config(self):
        return self.config.get("api", {
            "api_key": None,
            "base_url": None
        }) 