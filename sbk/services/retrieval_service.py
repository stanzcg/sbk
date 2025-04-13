from typing import List, Dict, Optional
from sbk.services.vector_service import VectorService
from sbk.models.schemas import Query
import logging  # 添加日志模块

from sbk.core.embeddings.factory import EmbeddingFactory

# 配置日志
logger = logging.getLogger(__name__)

class RetrievalService:
    def __init__(self, 
                 kb_id: int,
                 retrieval_config: Optional[Dict] = None,
                 config: Optional[Dict] = None):
        """初始化检索服务
        
        Args:
            vector_store_path: 向量库路径
            retrieval_config: 检索配置
            api_config: API配置
        """
        self.kb_id = kb_id
        self.retrieval_config = retrieval_config or {
            "type": "hybrid",
            "vector_weight": 0.7,
            "bm25_weight": 0.3
        }
        self.config = config or {}
        self.vector_service = VectorService(collection_name=f"collection_kb_{self.kb_id}")
        self.embedding_model = None  # 初始化 embedding_model 属性
        
    def search(self, query: Query, top_k: int = 3) -> List[Dict]:
        """检索相关文档片段
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            
        Returns:
            List[Dict]: 检索结果列表
        """
        logger.debug(f"开始检索: query='{query.query}', top_k={top_k}")  # 添加日志
        # 根据检索类型执行不同的检索策略
        retrieval_type = self.retrieval_config.get("type", "hybrid")
        
        if retrieval_type == "bm25":
            results = self._bm25_search(query, top_k)
        else:  # hybridx
            if not getattr(self, "embedding_model"):
                self.embedding_model = EmbeddingFactory.create(self.config.get("embedding"))
            query.embeddings = self.embedding_model.embed_documents(query.query)
            if retrieval_type == "vector":
                results = self._vector_search(query, top_k)
            else:
                vector_results = self._vector_search(query, top_k)
                bm25_results = self._bm25_search(query, top_k)
                results = self._hybrid_merge(vector_results, bm25_results)

        return results[:top_k]
    
    def _vector_search(self, query: Query, top_k: int) -> List[Dict]:
        """执行向量检索"""
        logger.debug(f"执行向量检索: query='{query.query}', top_k={top_k}")  # 添加日志
        # 使用向量服务进行检索
        results = self.vector_service.search(query=query, top_k=top_k)
        
        return results
    
    def _bm25_search(self, query: Query, top_k: int) -> List[Dict]:
        """执行BM25检索"""
        logger.debug(f"执行BM25检索: query='{query.query}', top_k={top_k}")  # 添加日志
        # TODO: 实现BM25检索
        return []
    
    def _hybrid_merge(self, vector_results: List[Dict], bm25_results: List[Dict]) -> List[Dict]:
        """合并向量检索和BM25检索的结果"""
        logger.debug("合并检索结果")  # 添加日志
        vector_weight = self.retrieval_config.get("vector_weight", 0.7)
        bm25_weight = self.retrieval_config.get("bm25_weight", 0.3)
        
        # 创建结果映射
        merged_results = {}
        logger.debug(len(vector_results))
        logger.debug(len(bm25_results))
        
        # 处理向量检索结果
        for result in vector_results:
            id = result["id"]
            merged_results[id] = {
                "doc_id": result["doc_id"],
                "metadata": result["metadata"],
                "score": result["score"] * vector_weight,
                "content": result["content"], 
            }
        
        # 处理BM25检索结果
        for result in bm25_results:
            id = result["id"]
            if id in merged_results:
                merged_results[id]["score"] += result["score"] * bm25_weight
            else:
                merged_results[id] = {
                    "doc_id": result["doc_id"],
                    "metadata": result["metadata"],
                    "score": result["score"] * bm25_weight,
                    "content": result["content"],
                }
        
        # 按分数排序
        sorted_results = sorted(
            merged_results.values(),
            key=lambda x: x["score"],
            reverse=True
        )
        
        return sorted_results 