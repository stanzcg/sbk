import json
from typing import List, Dict, Optional, Union
import logging
from pymilvus import (
    connections,
    utility,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType
)
from sbk.core.exceptions import VectorStoreError, ResourceNotFoundError
from sbk.models.schemas import Query


logger = logging.getLogger(__name__)

class VectorService:
    def __init__(self, 
                 host: str = "localhost",
                 port: str = "19530",
                 collection_name: str = None,
                 dim: int = 1024,
                 kb_name: str = "default",
                 index_params: dict = None):
        """初始化向量服务
        
        Args:
            host: Milvus服务器地址
            port: Milvus服务器端口
            collection_name: 集合名称，如果为None则使用默认名称
            dim: 向量维度
        """
        self.host = host
        self.port = port
        self.collection_name = collection_name or "document_segments"
        self.dim = dim
        self.kb_name = kb_name
        self.index_params = index_params or {
                "metric_type": "L2",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 8}
            }
        
        try:
            connections.connect(kb_name=kb_name, host=self.host, port=self.port)
            logger.debug("Connected to Milvus server at %s:%s", self.host, self.port)
            
            if not utility.has_collection(self.collection_name):
                self._create_collection()
                
            self.collection = Collection(self.collection_name)
        except Exception as e:
            logger.error("Failed to initialize vector service: %s", str(e))
            raise VectorStoreError(f"Failed to initialize vector service: {str(e)}")
        
    def _create_collection(self):
        """创建Milvus collection"""
        try:
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=200),
                FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name="metadata", dtype=DataType.JSON),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dim)
            ]
            schema = CollectionSchema(fields=fields, description="Document segments for RAG")
            collection = Collection(name=self.collection_name, schema=schema)
            
            # 创建索引
            collection.create_index(field_name="embedding", index_params=self.index_params)
            
            # 创建node_id索引
            collection.create_index(field_name="doc_id")
            
        except Exception as e:
            raise VectorStoreError(f"Failed to create collection: {str(e)}")
        
    def add_documents(self, 
                     embeddings: List[List[float]], 
                     contents: List[str],
                     metadatas: List[Dict],
                     doc_ids: Optional[List[str]] = None) -> List[str]:
        """添加文档到向量库
        
        Args:
            embeddings: 文档向量列表
            metadata_list: 元数据列表，每个元素应包含file_hash和content等信息
            node_ids: 节点ID列表，如果为None则自动生成
            
        Returns:
            List[str]: 节点ID列表
        """
        try:
            if len(embeddings) != len(metadatas):
                raise ValueError("embeddings和metadata_list长度必须相同")
                
            
            if len(doc_ids) != len(embeddings):
                raise ValueError("node_ids长度必须与embeddings相同")
            
            entities = [
                {
                    "doc_id": doc_id,
                    "metadata": metadata,
                    "embedding": embedding,
                    "content": content
                }
                for doc_id, content, metadata, embedding in zip(doc_ids, contents, metadatas, embeddings)
            ]
            
            self.collection.insert(entities)
            self.collection.flush()
            
        except Exception as e:
            raise VectorStoreError(f"Failed to add documents: {str(e)}")
        
    def search(self, 
              query: Query,
              metadata_filter: Optional[Dict] = None,
              top_k: int = 3) -> List[Dict]:
        """搜索相似文档
        
        Args:
            embedding: 查询向量
            metadata_filter: 元数据过滤条件
            top_k: 返回结果数量
            
        Returns:
            List[Dict]: 搜索结果列表
        """
        try:
            self.collection.load()
            
            # 构建查询条件
            filter_expr = None
            if metadata_filter:
                filter_conditions = []
                for key, value in metadata_filter.items():
                    if isinstance(value, str):
                        filter_conditions.append(f'metadata["{key}"] == "{value}"')
                    else:
                        filter_conditions.append(f'metadata["{key}"] == {value}')
                if filter_conditions:
                    filter_expr = " && ".join(filter_conditions)
            
            # 执行向量检索
            search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
            results = self.collection.search(
                data=query.embeddings,
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                expr=filter_expr,
                output_fields=["doc_id", "metadata", "content", "id"]
            )
            
            # 格式化结果
            hits = []
            for hit in results[0]:
                hits.append({
                    "score": float(hit.score),
                    "doc_id": hit.entity.get("doc_id"),
                    "metadata": hit.entity.get("metadata"),
                    "content": hit.entity.get("content"),
                    "id": hit.entity.get("id"),
                })
            
            return hits
            
        except Exception as e:
            raise VectorStoreError(f"Search failed: {str(e)}")
    
    def delete_by_metadata(self, metadata_filter: Dict) -> int:
        """根据元数据条件删除向量"""
        try:
            filter_conditions = []
            for key, value in metadata_filter.items():
                if isinstance(value, str):
                    filter_conditions.append(f'metadata["{key}"] == "{value}"')
                else:
                    filter_conditions.append(f'metadata["{key}"] == {value}')
            
            expr = " && ".join(filter_conditions)
            return self._delete_entities(expr)
        except Exception as e:
            raise VectorStoreError(f"Failed to delete by metadata: {str(e)}")
    
    def delete_by_id(self, id: int) -> int:
        """根据节点ID删除向量"""
        try:
            expr = f'id == "{id}"'
            return self._delete_entities(expr)
        except Exception as e:
            raise VectorStoreError(f"Failed to delete by node ID: {str(e)}")
        
    def delete_by_doc_id(self, doc_id: str) -> int:
        """根据节点ID删除向量"""
        try:
            expr = f'doc_id == "{doc_id}"'
            return self._delete_entities(expr)
        except Exception as e:
            raise VectorStoreError(f"Failed to delete by node ID: {str(e)}") 
    
    def _delete_entities(self, expr: str) -> int:
        """删除符合条件的实体
        
        Args:
            expr: 删除条件表达式
            
        Returns:
            int: 删除的实体数量
        """
        try:
            self.collection.load()
            # 先查询匹配的实体数量
            count = self.collection.query(expr=expr, output_fields=["count(*)"])[0]["count"]
            if count > 0:
                self.collection.delete(expr)
                self.collection.flush()
            return count
        except Exception as e:
            raise VectorStoreError(f"Delete operation failed: {str(e)}")
            
    def __del__(self):
        """析构函数，确保关闭连接"""
        try:
            if utility.has_collection(self.collection_name):
                self.collection.release()
            connections.disconnect("default")
        except Exception as e:
            logger.error("Error during disconnection: %s", str(e)) 