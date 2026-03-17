from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, LearningRecord, Poem, User
from datetime import datetime, timedelta
import json

learning_bp = Blueprint('learning', __name__)

@learning_bp.route('/records', methods=['GET'])
@jwt_required()
def get_learning_records():
    """获取用户学习记录"""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        poem_id = request.args.get('poem_id', type=int)
        
        query = LearningRecord.query.filter_by(user_id=user_id)
        
        if poem_id:
            query = query.filter_by(poem_id=poem_id)
        
        records = query.order_by(LearningRecord.last_visit.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 包含诗歌信息
        records_with_poems = []
        for record in records.items:
            record_dict = record.to_dict()
            poem = Poem.query.get(record.poem_id)
            if poem:
                record_dict['poem'] = {
                    'title': poem.title,
                    'author': poem.author,
                    'dynasty': poem.dynasty
                }
            records_with_poems.append(record_dict)
        
        return jsonify({
            'learning_records': records_with_poems,
            'total': records.total,
            'pages': records.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@learning_bp.route('/records/<int:poem_id>', methods=['GET'])
@jwt_required()
def get_poem_learning_record(poem_id):
    """获取特定古诗的学习记录"""
    try:
        user_id = get_jwt_identity()
        
        record = LearningRecord.query.filter_by(
            user_id=user_id, poem_id=poem_id
        ).first()
        
        if not record:
            return jsonify({'error': 'Learning record not found'}), 404
        
        record_dict = record.to_dict()
        
        # 解析字词查询记录
        if record.word_queries:
            try:
                record_dict['word_queries'] = json.loads(record.word_queries)
            except json.JSONDecodeError:
                record_dict['word_queries'] = []
        else:
            record_dict['word_queries'] = []
        
        return jsonify({'learning_record': record_dict}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@learning_bp.route('/records/<int:poem_id>/complete', methods=['POST'])
@jwt_required()
def complete_poem_learning(poem_id):
    """标记古诗学习完成"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        record = LearningRecord.query.filter_by(
            user_id=user_id, poem_id=poem_id
        ).first()
        
        if not record:
            return jsonify({'error': 'Learning record not found'}), 404
        
        # 更新完成状态
        record.is_completed = True
        record.completion_rate = data.get('completion_rate', 1.0)
        record.last_visit = datetime.utcnow()
        
        # 更新用户统计数据
        user = User.query.get(user_id)
        if user and not record.is_completed:  # 避免重复计算
            user.poems_studied += 1
        
        db.session.commit()
        
        return jsonify({
            'message': 'Poem learning completed',
            'learning_record': record.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@learning_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_learning_statistics():
    """获取学习统计数据"""
    try:
        user_id = get_jwt_identity()
        
        # 基本统计
        total_records = LearningRecord.query.filter_by(user_id=user_id).count()
        completed_poems = LearningRecord.query.filter_by(
            user_id=user_id, is_completed=True
        ).count()
        
        # 总学习时间（分钟）
        total_time_result = db.session.query(
            db.func.sum(LearningRecord.reading_time + 
                       LearningRecord.video_watch_time + 
                       LearningRecord.audio_listen_time)
        ).filter_by(user_id=user_id).scalar()
        
        total_study_time = (total_time_result or 0) // 60  # 转换为分钟
        
        # 最近7天的学习活动
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_activity = LearningRecord.query.filter(
            LearningRecord.user_id == user_id,
            LearningRecord.last_visit >= seven_days_ago
        ).count()
        
        # 学习进度分布
        difficulty_stats = db.session.query(
            Poem.difficulty_level,
            db.func.count(LearningRecord.id).label('count')
        ).join(LearningRecord).filter(
            LearningRecord.user_id == user_id,
            LearningRecord.is_completed == True
        ).group_by(Poem.difficulty_level).all()
        
        difficulty_distribution = {str(stat[0]): stat[1] for stat in difficulty_stats}
        
        # 朝代分布
        dynasty_stats = db.session.query(
            Poem.dynasty,
            db.func.count(LearningRecord.id).label('count')
        ).join(LearningRecord).filter(
            LearningRecord.user_id == user_id,
            LearningRecord.is_completed == True
        ).group_by(Poem.dynasty).all()
        
        dynasty_distribution = {stat[0]: stat[1] for stat in dynasty_stats}
        
        return jsonify({
            'total_poems_accessed': total_records,
            'completed_poems': completed_poems,
            'total_study_time_minutes': total_study_time,
            'recent_activity_count': recent_activity,
            'difficulty_distribution': difficulty_distribution,
            'dynasty_distribution': dynasty_distribution,
            'completion_rate': (completed_poems / total_records * 100) if total_records > 0 else 0
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@learning_bp.route('/daily-stats', methods=['GET'])
@jwt_required()
def get_daily_learning_stats():
    """获取每日学习统计（最近30天）"""
    try:
        user_id = get_jwt_identity()
        days = request.args.get('days', 30, type=int)
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 按日期分组统计学习时间
        daily_stats = db.session.query(
            db.func.date(LearningRecord.last_visit).label('date'),
            db.func.sum(LearningRecord.reading_time + 
                       LearningRecord.video_watch_time + 
                       LearningRecord.audio_listen_time).label('total_time'),
            db.func.count(db.distinct(LearningRecord.poem_id)).label('poems_studied')
        ).filter(
            LearningRecord.user_id == user_id,
            LearningRecord.last_visit >= start_date
        ).group_by(db.func.date(LearningRecord.last_visit)).all()
        
        # 格式化数据
        daily_data = []
        for stat in daily_stats:
            daily_data.append({
                'date': stat.date.isoformat(),
                'study_time_minutes': (stat.total_time or 0) // 60,
                'poems_studied': stat.poems_studied
            })
        
        return jsonify({'daily_stats': daily_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@learning_bp.route('/word-frequency', methods=['GET'])
@jwt_required()
def get_word_query_frequency():
    """获取高频查询字词统计"""
    try:
        user_id = get_jwt_identity()
        limit = request.args.get('limit', 20, type=int)
        
        # 获取所有字词查询记录
        records = LearningRecord.query.filter_by(user_id=user_id).all()
        
        word_count = {}
        for record in records:
            if record.word_queries:
                try:
                    queries = json.loads(record.word_queries)
                    for word in queries:
                        word_count[word] = word_count.get(word, 0) + 1
                except json.JSONDecodeError:
                    continue
        
        # 排序并限制数量
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        return jsonify({
            'word_frequency': [{'word': word, 'count': count} for word, count in sorted_words]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@learning_bp.route('/progress-report', methods=['GET'])
@jwt_required()
def generate_progress_report():
    """生成学习进度报告"""
    try:
        user_id = get_jwt_identity()
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # 获取详细统计数据
        total_records = LearningRecord.query.filter_by(user_id=user_id).count()
        completed_poems = LearningRecord.query.filter_by(
            user_id=user_id, is_completed=True
        ).count()
        
        # 平均学习时间
        avg_time_result = db.session.query(
            db.func.avg(LearningRecord.reading_time + 
                       LearningRecord.video_watch_time + 
                       LearningRecord.audio_listen_time)
        ).filter_by(user_id=user_id).scalar()
        
        avg_study_time = (avg_time_result or 0) // 60  # 转换为分钟
        
        # 学习活跃度（最近30天）
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_days = db.session.query(
            db.func.count(db.distinct(db.func.date(LearningRecord.last_visit)))
        ).filter(
            LearningRecord.user_id == user_id,
            LearningRecord.last_visit >= thirty_days_ago
        ).scalar()
        
        # 最喜欢的朝代
        favorite_dynasty = db.session.query(
            Poem.dynasty,
            db.func.count(LearningRecord.id).label('count')
        ).join(LearningRecord).filter(
            LearningRecord.user_id == user_id
        ).group_by(Poem.dynasty).order_by(db.desc('count')).first()
        
        report = {
            'user_info': user.to_dict(),
            'learning_summary': {
                'total_poems_accessed': total_records,
                'completed_poems': completed_poems,
                'completion_rate': (completed_poems / total_records * 100) if total_records > 0 else 0,
                'total_study_time_minutes': user.total_study_time,
                'average_study_time_per_poem': avg_study_time,
                'active_days_last_30': active_days,
                'favorite_dynasty': favorite_dynasty[0] if favorite_dynasty else None
            },
            'generated_at': datetime.utcnow().isoformat()
        }
        
        return jsonify(report), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
