from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Poem, LearningRecord
import json

poems_bp = Blueprint('poems', __name__)

@poems_bp.route('/', methods=['GET'])
def get_poems():
    """获取古诗列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        difficulty = request.args.get('difficulty', type=int)
        dynasty = request.args.get('dynasty')
        search = request.args.get('search')
        
        query = Poem.query
        
        # 筛选条件
        if difficulty:
            query = query.filter_by(difficulty_level=difficulty)
        
        if dynasty:
            query = query.filter_by(dynasty=dynasty)
        
        if search:
            query = query.filter(
                db.or_(
                    Poem.title.contains(search),
                    Poem.author.contains(search),
                    Poem.content.contains(search)
                )
            )
        
        poems = query.order_by(Poem.id).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'poems': [poem.to_dict() for poem in poems.items],
            'total': poems.total,
            'pages': poems.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@poems_bp.route('/<int:poem_id>', methods=['GET'])
def get_poem(poem_id):
    """获取单首古诗详情"""
    try:
        poem = Poem.query.get(poem_id)
        if not poem:
            return jsonify({'error': 'Poem not found'}), 404
        
        poem_data = poem.to_dict()
        
        # 解析注释JSON
        if poem.annotations:
            try:
                poem_data['annotations'] = json.loads(poem.annotations)
            except json.JSONDecodeError:
                poem_data['annotations'] = {}
        else:
            poem_data['annotations'] = {}
        
        return jsonify({'poem': poem_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@poems_bp.route('/<int:poem_id>/start-learning', methods=['POST'])
@jwt_required()
def start_learning(poem_id):
    """开始学习一首古诗"""
    try:
        user_id = get_jwt_identity()
        
        poem = Poem.query.get(poem_id)
        if not poem:
            return jsonify({'error': 'Poem not found'}), 404
        
        # 查找或创建学习记录
        learning_record = LearningRecord.query.filter_by(
            user_id=user_id, poem_id=poem_id
        ).first()
        
        if not learning_record:
            learning_record = LearningRecord(
                user_id=user_id,
                poem_id=poem_id
            )
            db.session.add(learning_record)
        else:
            # 更新最后访问时间
            from datetime import datetime
            learning_record.last_visit = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Learning session started',
            'learning_record': learning_record.to_dict(),
            'poem': poem.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@poems_bp.route('/<int:poem_id>/track-reading', methods=['POST'])
@jwt_required()
def track_reading_time(poem_id):
    """追踪阅读时间"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'reading_time' not in data:
            return jsonify({'error': 'reading_time is required'}), 400
        
        learning_record = LearningRecord.query.filter_by(
            user_id=user_id, poem_id=poem_id
        ).first()
        
        if not learning_record:
            return jsonify({'error': 'Learning record not found'}), 404
        
        # 更新阅读时间
        learning_record.reading_time += data['reading_time']
        
        # 更新字词查询记录
        if 'word_queries' in data:
            existing_queries = json.loads(learning_record.word_queries or '[]')
            existing_queries.extend(data['word_queries'])
            learning_record.word_queries = json.dumps(existing_queries)
        
        # 更新最后访问时间
        from datetime import datetime
        learning_record.last_visit = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Reading time tracked successfully',
            'learning_record': learning_record.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@poems_bp.route('/<int:poem_id>/track-media', methods=['POST'])
@jwt_required()
def track_media_time(poem_id):
    """追踪多媒体观看时间"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        learning_record = LearningRecord.query.filter_by(
            user_id=user_id, poem_id=poem_id
        ).first()
        
        if not learning_record:
            return jsonify({'error': 'Learning record not found'}), 404
        
        # 更新视频观看时间
        if 'video_watch_time' in data:
            learning_record.video_watch_time += data['video_watch_time']
        
        # 更新音频收听时间
        if 'audio_listen_time' in data:
            learning_record.audio_listen_time += data['audio_listen_time']
        
        # 更新最后访问时间
        from datetime import datetime
        learning_record.last_visit = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Media time tracked successfully',
            'learning_record': learning_record.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@poems_bp.route('/dynasties', methods=['GET'])
def get_dynasties():
    """获取所有朝代列表"""
    try:
        dynasties = db.session.query(Poem.dynasty).distinct().all()
        dynasty_list = [dynasty[0] for dynasty in dynasties]
        
        return jsonify({'dynasties': dynasty_list}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@poems_bp.route('/authors', methods=['GET'])
def get_authors():
    """获取所有作者列表"""
    try:
        authors = db.session.query(Poem.author, Poem.dynasty).distinct().all()
        author_list = [{'name': author[0], 'dynasty': author[1]} for author in authors]
        
        return jsonify({'authors': author_list}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@poems_bp.route('/recommend', methods=['GET'])
@jwt_required()
def recommend_poems():
    """基于用户学习记录推荐古诗"""
    try:
        user_id = get_jwt_identity()
        limit = request.args.get('limit', 5, type=int)
        
        # 获取用户已学习的诗歌
        learned_poem_ids = db.session.query(LearningRecord.poem_id).filter_by(
            user_id=user_id
        ).subquery()
        
        # 推荐未学习的诗歌，按难度递增
        recommended_poems = Poem.query.filter(
            ~Poem.id.in_(learned_poem_ids)
        ).order_by(Poem.difficulty_level, Poem.id).limit(limit).all()
        
        return jsonify({
            'recommended_poems': [poem.to_dict() for poem in recommended_poems]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
