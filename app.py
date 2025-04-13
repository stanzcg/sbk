import os

from flask import Flask, request, jsonify
from kbs.services.document_service import DocumentService
from kbs.services.vector_service import VectorService
from kbs.services.retrieval_service import RetrievalService
from kbs.services.knowledge_base_service import KnowledgeBaseService
from kbs.core.database import get_db, engine, Base
from kbs.models.schemas import KnowledgeBaseConfig, SearchRequest, Query
from kbs.core.exceptions import ValidationError

app = Flask(__name__)

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 知识库管理
@app.route('/knowledge-bases/create', methods=['POST'])
def create_knowledge_base():
    try:
        data = request.json
        if not data or 'name' not in data:
            return jsonify({'error': 'Name is required'}), 400
        
        # 验证配置
        config = data.get('config', {})
        try:
            validated_config = KnowledgeBaseConfig(**config).model_dump()
        except Exception as e:
            raise ValidationError(f"Invalid config: {str(e)}")
            
        db = next(get_db())
        kb_service = KnowledgeBaseService(db)
        kb = kb_service.create_knowledge_base(
            name=data['name'],
            description=data.get('description'),
            config=validated_config,
        )
        
        return jsonify({
            'id': kb.id,
            'name': kb.name,
            'description': kb.description,
            'config': kb.config
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/knowledge-bases/list', methods=['GET'])
def list_knowledge_bases():
    try:
        db = next(get_db())
        kb_service = KnowledgeBaseService(db)
        kbs = kb_service.list_knowledge_bases()
        
        return jsonify([{
            'id': kb.id,
            'name': kb.name,
            'description': kb.description,
            'config': kb.config
        } for kb in kbs]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 文档上传和处理
@app.route('/knowledge-bases/<int:kb_id>/documents/upload', methods=['POST'])
def upload_document(kb_id):
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        db = next(get_db())
        kb_service = KnowledgeBaseService(db)
        kb = kb_service.get_knowledge_base(kb_id)
        
        if not kb:
            return jsonify({'error': 'Knowledge base not found'}), 404
            
        doc_service = DocumentService(kb.id, kb.document_store_path, kb.vector_store_path, kb.config)
        doc_id = doc_service.process_document(file)
        
        return jsonify({
            'message': 'Document uploaded and processed successfully',
            'document_id': doc_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 文档检索
@app.route('/knowledge-bases/<int:kb_id>/search', methods=['POST'])
def search(kb_id):
    try:
        # 验证搜索请求
        try:
            search_request = SearchRequest(**request.json)
        except Exception as e:
            raise ValidationError(f"Invalid search request: {str(e)}")
            
        db = next(get_db())
        kb_service = KnowledgeBaseService(db)
        kb = kb_service.get_knowledge_base(kb_id)
        
        if not kb:
            return jsonify({'error': 'Knowledge base not found'}), 404
            
        retrieval_service = RetrievalService(
            kb.id,
            search_request.retrieval_config.model_dump() if search_request.retrieval_config else None,
            kb.config,
        )
        query = Query(query=search_request.query)
        results = retrieval_service.search(query, search_request.top_k)
        
        return jsonify({
            'results': results
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('kbs_server_port', 9159)) 