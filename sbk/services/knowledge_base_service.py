import os
from sqlalchemy.orm import Session
from sbk.models.knowledge_base import KnowledgeBase

class KnowledgeBaseService:
    def __init__(self, db: Session):
        self.db = db
        self.base_vector_path = "data/vector_stores"
        self.base_document_path = "data/documents"
        
        # 确保基础目录存在
        os.makedirs(self.base_vector_path, exist_ok=True)
        os.makedirs(self.base_document_path, exist_ok=True)

    def create_knowledge_base(self, name: str, description: str = None, config: dict = {}) -> KnowledgeBase:
        """创建新的知识库"""
        kb = KnowledgeBase(
            name=name,
            description=description,
            vector_store_path=os.path.join(self.base_vector_path, name),
            document_store_path=os.path.join(self.base_document_path, name),
            config=config
        )
        
        self.db.add(kb)
        self.db.commit()
        self.db.refresh(kb)
        
        # 创建知识库对应的文件夹
        os.makedirs(kb.vector_store_path, exist_ok=True)
        os.makedirs(kb.document_store_path, exist_ok=True)
        
        return kb

    def get_knowledge_base(self, kb_id: int) -> KnowledgeBase:
        """获取知识库信息"""
        return self.db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()

    def list_knowledge_bases(self, skip: int = 0, limit: int = 100):
        """列出所有知识库"""
        return self.db.query(KnowledgeBase).offset(skip).limit(limit).all()

    def delete_knowledge_base(self, kb_id: int):
        """删除知识库"""
        kb = self.get_knowledge_base(kb_id)
        if kb:
            # 删除文件夹
            if os.path.exists(kb.vector_store_path):
                os.rmdir(kb.vector_store_path)
            if os.path.exists(kb.document_store_path):
                os.rmdir(kb.document_store_path)
                
            self.db.delete(kb)
            self.db.commit()
            return True
        return False 