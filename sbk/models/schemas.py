from typing import Optional, Union
from pydantic import BaseModel, Field

class EmbeddingConfig(BaseModel):
    type: str = Field(
        default="sentence_transformer",
        description="embedding类型，支持 sentence_transformer 和 openai"
    )
    model_name: str = Field(
        default="all-MiniLM-L6-v2",
        description="模型名称"
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API密钥，当type为openai时需要"
    )
    base_url: Optional[str] = Field(
        default=None,
        description="API基础URL，当type为openai时可选"
    )

class RetrievalConfig(BaseModel):
    type: str = Field(
        default="hybrid",
        description="检索类型：hybrid, vector, bm25"
    )
    vector_weight: float = Field(
        default=0.7,
        description="向量检索权重",
        ge=0,
        le=1
    )
    bm25_weight: float = Field(
        default=0.3,
        description="BM25检索权重",
        ge=0,
        le=1
    )

class APIConfig(BaseModel):
    api_key: Optional[str] = Field(
        default=None,
        description="API密钥"
    )
    base_url: Optional[str] = Field(
        default=None,
        description="API基础URL"
    )

class KnowledgeBaseConfig(BaseModel):
    embedding: EmbeddingConfig = Field(
        default_factory=EmbeddingConfig,
        description="Embedding配置"
    )

class SearchRequest(BaseModel):
    query: Union[str, list] = Field(..., description="搜索查询")
    top_k: Union[int, list[int]] = Field(default=3, description="返回结果数量")
    retrieval_config: Optional[RetrievalConfig] = Field(
        default_factory=RetrievalConfig,
        description="检索配置"
    )
    api_config: Optional[APIConfig] = Field(
        default_factory=APIConfig,
        description="API配置"
    ) 

class Query(BaseModel):
    query: Union[str, list] = Field(..., description="用户查询")
    embeddings: Union[list, list[list[float]], None] = Field(default=None, description="查询的embedding")