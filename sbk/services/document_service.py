import os
import uuid
from typing import List, Dict
from werkzeug.datastructures import FileStorage
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredFileLoader
)
import logging

from sbk.core.embeddings.factory import EmbeddingFactory

# 配置日志记录
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self, kb_id: int, document_store_path: str, vector_store_path: str, config: dict):
        self.kb_id = kb_id
        self.document_store_path = document_store_path
        self.vector_store_path = vector_store_path
        self.SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.txt'}
        self.embedding_config = config.get("embedding")
        logger.debug(f"kb_id: {self.kb_id}, embedding_config: {self.embedding_config}")
        self.embedding_model = EmbeddingFactory.create(self.embedding_config)
        logger.debug("DocumentService initialized with store paths: %s, %s", document_store_path, vector_store_path)
        
    def process_document(self, file: FileStorage) -> str:
        """处理上传的文档
        
        Args:
            file: 上传的文件对象
            
        Returns:
            str: 文档ID
        """
        logger.debug("Processing document: %s", file.filename)
        doc_id = str(uuid.uuid4())
        logger.debug("Generated document ID: %s", doc_id)
        
        # 保存文件
        filename = file.filename
        ext = os.path.splitext(filename)[1].lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            logger.error("Unsupported file type: %s", ext)
            raise ValueError(f'Unsupported file type: {ext}')
            
        file_path = os.path.join(self.document_store_path, f'{doc_id}{ext}')
        logger.debug("Saving file to: %s", file_path)
        file.save(file_path)
        
        try:
            # 加载文档
            logger.debug("Loading document...")
            if ext == '.pdf':
                loader = PyPDFLoader(file_path)
            elif ext == '.docx':
                loader = Docx2txtLoader(file_path)
            else:
                loader = UnstructuredFileLoader(file_path)
                
            documents = loader.load()
            logger.debug("Loaded %d documents", len(documents))
            
            # 文本分段
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )
            splits = text_splitter.split_documents(documents)
            logger.debug("Split documents into %d chunks", len(splits))
            
            # 向量化存储
            from sbk.services.vector_service import VectorService
            texts = [chunk.page_content for chunk in splits]
            embeddings = self.embedding_model.embed_documents(texts=texts)
            metadatas = [chunk.metadata for chunk in splits]
            doc_ids = [file.filename for _ in range(len(texts))]
            vector_service = VectorService(collection_name=f"collection_kb_{self.kb_id}", dim=len(embeddings[0]))
            vector_service.add_documents(embeddings=embeddings, contents=texts, metadatas=metadatas, doc_ids=doc_ids)
            logger.debug("Added documents to vector service with ID: %s", doc_id)
            
            return doc_id
            
        finally:
            logger.debug("Cleaning up temporary file: %s", file_path)
            # 清理临时文件
            os.remove(file_path)
            
    def get_document_metadata(self, doc_id: str) -> Dict:
        """获取文档元数据
        
        Args:
            doc_id: 文档ID
            
        Returns:
            Dict: 文档元数据
        """
        logger.debug("Fetching metadata for document ID: %s", doc_id)
        # TODO: 实现从数据库获取文档元数据
        return {
            'id': doc_id,
            'status': 'processed'
        } 