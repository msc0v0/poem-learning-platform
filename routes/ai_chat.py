from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, QARecord, Poem
from services.qwen_service import QwenService

ai_chat_bp = Blueprint('ai_chat', __name__)
qwen_service = QwenService()

@ai_chat_bp.route('/word-analysis', methods=['POST'])
@jwt_required()
def analyze_word():
    """分析古诗中的字词"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('poem_id'):
            return jsonify({'error': 'poem_id is required'}), 400
        
        # 获取诗歌信息
        poem = Poem.query.get(data['poem_id'])
        if not poem:
            return jsonify({'error': 'Poem not found'}), 404
        
        # 如果没有指定字词，让AI自动解析重要字词
        word = data.get('word', None)
        
        # 调用AI服务分析字词
        result = qwen_service.analyze_poem_word(poem.title, poem.content, word)
        
        if not result['success']:
            return jsonify({'error': result['error']}), 500
        
        # 保存问答记录
        question_text = f"请解释字词：{word}" if word else "请解析这首诗中的重要字词"
        qa_record = QARecord(
            user_id=user_id,
            poem_id=poem.id,
            question=question_text,
            answer=result['content'],
            question_type='字词解析',
            response_time=result['response_time']
        )
        db.session.add(qa_record)
        db.session.commit()
        
        return jsonify({
            'answer': result['content'],
            'response_time': result['response_time'],
            'qa_id': qa_record.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ai_chat_bp.route('/background-explanation', methods=['POST'])
@jwt_required()
def explain_background():
    """解释古诗创作背景"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('poem_id'):
            return jsonify({'error': 'poem_id is required'}), 400
        
        # 获取诗歌信息
        poem = Poem.query.get(data['poem_id'])
        if not poem:
            return jsonify({'error': 'Poem not found'}), 404
        
        # 调用AI服务解释背景
        result = qwen_service.explain_poem_background(poem.title, poem.author, poem.content)
        
        if not result['success']:
            return jsonify({'error': result['error']}), 500
        
        # 保存问答记录
        qa_record = QARecord(
            user_id=user_id,
            poem_id=poem.id,
            question="请介绍这首诗的创作背景",
            answer=result['content'],
            question_type='背景介绍',
            response_time=result['response_time']
        )
        db.session.add(qa_record)
        db.session.commit()
        
        return jsonify({
            'answer': result['content'],
            'response_time': result['response_time'],
            'qa_id': qa_record.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ai_chat_bp.route('/artistic-analysis', methods=['POST'])
@jwt_required()
def analyze_artistic_conception():
    """分析古诗意境"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('poem_id'):
            return jsonify({'error': 'poem_id is required'}), 400
        
        # 获取诗歌信息
        poem = Poem.query.get(data['poem_id'])
        if not poem:
            return jsonify({'error': 'Poem not found'}), 404
        
        # 调用AI服务分析意境
        result = qwen_service.analyze_poem_artistic_conception(poem.title, poem.author, poem.content)
        
        if not result['success']:
            return jsonify({'error': result['error']}), 500
        
        # 保存问答记录
        qa_record = QARecord(
            user_id=user_id,
            poem_id=poem.id,
            question="请分析这首诗的意境和艺术特色",
            answer=result['content'],
            question_type='意境赏析',
            response_time=result['response_time']
        )
        db.session.add(qa_record)
        db.session.commit()
        
        return jsonify({
            'answer': result['content'],
            'response_time': result['response_time'],
            'qa_id': qa_record.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ai_chat_bp.route('/general-question', methods=['POST'])
@jwt_required()
def answer_general_question():
    """回答一般问题（旧版，保持兼容）"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('question'):
            return jsonify({'error': 'question is required'}), 400
        
        poem_context = None
        poem_id = data.get('poem_id')
        
        # 如果指定了诗歌ID，获取诗歌上下文
        if poem_id:
            poem = Poem.query.get(poem_id)
            if poem:
                poem_context = f"《{poem.title}》- {poem.author}\n{poem.content}"
        
        # 调用AI服务回答问题
        result = qwen_service.answer_general_question(data['question'], poem_context)
        
        if not result['success']:
            return jsonify({'error': result['error']}), 500
        
        # 保存问答记录
        qa_record = QARecord(
            user_id=user_id,
            poem_id=poem_id,
            question=data['question'],
            answer=result['content'],
            question_type='其他',
            response_time=result['response_time']
        )
        db.session.add(qa_record)
        db.session.commit()
        
        return jsonify({
            'answer': result['content'],
            'response_time': result['response_time'],
            'qa_id': qa_record.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ai_chat_bp.route('/ask', methods=['POST'])
@jwt_required()
def ask_multilingual_question():
    """智能多语言问答（新版）
    
    支持：
    1. 多语言提问（中文、英语、西语、法语等）
    2. HSK等级适配的中文回答
    3. 提供母语翻译（可选显示）
    4. 预设QA库快速响应
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('question'):
            return jsonify({'error': 'question is required'}), 400
        
        question = data['question']
        poem_id = data.get('poem_id')
        hsk_level = data.get('hsk_level', 'HSK3')  # 默认HSK3级别
        user_language = data.get('user_language')  # 用户母语（可选）
        
        # 验证HSK等级
        valid_levels = ['HSK1', 'HSK2', 'HSK3', 'HSK4', 'HSK5', 'HSK6']
        if hsk_level not in valid_levels:
            hsk_level = 'HSK3'
        
        # 获取诗歌上下文
        poem_context = None
        if poem_id:
            poem = Poem.query.get(poem_id)
            if poem:
                poem_context = f"《{poem.title}》- {poem.author}\n{poem.content}"
        
        # 调用智能问答服务
        result = qwen_service.answer_multilingual_question(
            question=question,
            poem_context=poem_context,
            hsk_level=hsk_level,
            user_language=user_language
        )
        
        if not result['success']:
            return jsonify({'error': result.get('error', 'Unknown error')}), 500
        
        # 保存问答记录
        qa_record = QARecord(
            user_id=user_id,
            poem_id=poem_id,
            question=question,
            answer=result['answer_chinese'],
            question_type='智能问答',
            response_time=result['response_time']
        )
        db.session.add(qa_record)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'answer_chinese': result['answer_chinese'],
            'answer_translation': result.get('answer_translation'),
            'has_translation': result.get('answer_translation') is not None,
            'question_language': result['question_language'],
            'user_language': result['user_language'],
            'common_qa_used': result['common_qa_used'],
            'hsk_level': hsk_level,
            'response_time': result['response_time'],
            'qa_id': qa_record.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ai_chat_bp.route('/common-questions', methods=['GET'])
def get_common_questions():
    """获取常见问题列表"""
    try:
        common_qa = qwen_service.common_qa
        
        # 按分类组织问题
        categories = {}
        for question, info in common_qa.items():
            category = info['category']
            if category not in categories:
                categories[category] = []
            categories[category].append({
                'question': question,
                'preview': info['answer'][:50] + '...' if len(info['answer']) > 50 else info['answer']
            })
        
        return jsonify({
            'success': True,
            'categories': categories,
            'total_questions': len(common_qa)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_chat_bp.route('/rate-answer', methods=['POST'])
@jwt_required()
def rate_answer():
    """评价AI回答质量"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('qa_id'):
            return jsonify({'error': 'qa_id is required'}), 400
        
        qa_record = QARecord.query.filter_by(id=data['qa_id'], user_id=user_id).first()
        if not qa_record:
            return jsonify({'error': 'QA record not found'}), 404
        
        # 更新评分
        if 'rating' in data:
            qa_record.user_rating = data['rating']
        
        if 'is_helpful' in data:
            qa_record.is_helpful = data['is_helpful']
        
        db.session.commit()
        
        return jsonify({'message': 'Rating updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ai_chat_bp.route('/history', methods=['GET'])
@jwt_required()
def get_qa_history():
    """获取用户的问答历史"""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        poem_id = request.args.get('poem_id', type=int)
        
        query = QARecord.query.filter_by(user_id=user_id)
        
        if poem_id:
            query = query.filter_by(poem_id=poem_id)
        
        qa_records = query.order_by(QARecord.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'qa_records': [record.to_dict() for record in qa_records.items],
            'total': qa_records.total,
            'pages': qa_records.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
