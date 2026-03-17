from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, LearningSession, InteractionEvent, Poem
from datetime import datetime, timedelta
import json

tracking_bp = Blueprint('tracking', __name__)

@tracking_bp.route('/session/start', methods=['POST'])
@jwt_required()
def start_session():
    """开始一个新的学习会话"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('poem_id'):
            return jsonify({'error': 'poem_id is required'}), 400
        
        poem_id = data.get('poem_id')
        
        # 检查诗歌是否存在
        poem = Poem.query.get(poem_id)
        if not poem:
            return jsonify({'error': 'Poem not found'}), 404
        
        # 创建新会话
        session = LearningSession(
            user_id=user_id,
            poem_id=poem_id,
            device_info=data.get('device_info', {}),
            interaction_data={
                'session_summary': {
                    'total_interactions': 0,
                    'active_time_seconds': 0,
                    'idle_time_seconds': 0,
                    'engagement_score': 0
                },
                'reading_behavior': {},
                'ai_interactions': {
                    'questions_asked': 0,
                    'topics': []
                },
                'exercise_attempts': {
                    'total_attempts': 0,
                    'correct_count': 0,
                    'time_spent_seconds': 0
                }
            }
        )
        
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'message': 'Session started',
            'session_id': session.id,
            'session': session.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@tracking_bp.route('/session/<int:session_id>/end', methods=['POST'])
@jwt_required()
def end_session(session_id):
    """结束学习会话"""
    try:
        user_id = get_jwt_identity()
        
        session = LearningSession.query.filter_by(
            id=session_id,
            user_id=user_id
        ).first()
        
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        data = request.get_json() or {}
        
        # 更新会话信息
        session.end_time = datetime.utcnow()
        session.duration_seconds = data.get('duration_seconds', 
            int((session.end_time - session.start_time).total_seconds()))
        session.is_completed = data.get('is_completed', False)
        session.completion_quality = data.get('completion_quality')
        
        db.session.commit()
        
        return jsonify({
            'message': 'Session ended',
            'session': session.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@tracking_bp.route('/event', methods=['POST'])
@jwt_required()
def track_event():
    """记录单个交互事件"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('event_type'):
            return jsonify({'error': 'event_type is required'}), 400
        
        session_id = data.get('session_id')
        
        # 如果提供了session_id，验证其有效性
        if session_id:
            session = LearningSession.query.filter_by(
                id=session_id,
                user_id=user_id
            ).first()
            if not session:
                return jsonify({'error': 'Invalid session_id'}), 400
        
        # 创建事件记录
        event = InteractionEvent(
            session_id=session_id,
            user_id=user_id,
            event_type=data.get('event_type'),
            event_target=data.get('event_target'),
            event_data=data.get('event_data', {}),
            page_context=data.get('page_context', {}),
            screen_position=data.get('screen_position')
        )
        
        db.session.add(event)
        
        # 更新会话的交互数据
        if session_id and session:
            interaction_data = session.interaction_data or {}
            summary = interaction_data.get('session_summary', {})
            summary['total_interactions'] = summary.get('total_interactions', 0) + 1
            interaction_data['session_summary'] = summary
            session.interaction_data = interaction_data
        
        db.session.commit()
        
        return jsonify({
            'message': 'Event tracked',
            'event_id': event.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@tracking_bp.route('/events/batch', methods=['POST'])
@jwt_required()
def track_events_batch():
    """批量记录交互事件（提高性能）"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('events'):
            return jsonify({'error': 'events array is required'}), 400
        
        events = data.get('events', [])
        session_id = data.get('session_id')
        
        # 验证session
        if session_id:
            session = LearningSession.query.filter_by(
                id=session_id,
                user_id=user_id
            ).first()
            if not session:
                return jsonify({'error': 'Invalid session_id'}), 400
        
        # 批量创建事件
        created_events = []
        for event_data in events:
            event = InteractionEvent(
                session_id=session_id,
                user_id=user_id,
                event_type=event_data.get('event_type'),
                event_target=event_data.get('event_target'),
                event_data=event_data.get('event_data', {}),
                page_context=event_data.get('page_context', {}),
                screen_position=event_data.get('screen_position'),
                timestamp=datetime.fromisoformat(event_data['timestamp']) 
                    if event_data.get('timestamp') else datetime.utcnow()
            )
            db.session.add(event)
            created_events.append(event)
        
        # 更新会话统计
        if session_id and session:
            interaction_data = session.interaction_data or {}
            summary = interaction_data.get('session_summary', {})
            summary['total_interactions'] = summary.get('total_interactions', 0) + len(events)
            interaction_data['session_summary'] = summary
            session.interaction_data = interaction_data
        
        db.session.commit()
        
        return jsonify({
            'message': 'Events tracked',
            'count': len(created_events)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@tracking_bp.route('/session/<int:session_id>/ai-interaction', methods=['POST'])
@jwt_required()
def track_ai_interaction(session_id):
    """记录AI问答交互"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        session = LearningSession.query.filter_by(
            id=session_id,
            user_id=user_id
        ).first()
        
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # 更新AI交互数据
        interaction_data = session.interaction_data or {}
        ai_interactions = interaction_data.get('ai_interactions', {
            'questions_asked': 0,
            'topics': [],
            'questions': []
        })
        
        ai_interactions['questions_asked'] = ai_interactions.get('questions_asked', 0) + 1
        
        # 记录问题详情
        if 'questions' not in ai_interactions:
            ai_interactions['questions'] = []
        
        ai_interactions['questions'].append({
            'question': data.get('question'),
            'topic': data.get('topic'),
            'timestamp': datetime.utcnow().isoformat(),
            'response_time': data.get('response_time')
        })
        
        # 更新话题列表
        topic = data.get('topic')
        if topic and topic not in ai_interactions.get('topics', []):
            if 'topics' not in ai_interactions:
                ai_interactions['topics'] = []
            ai_interactions['topics'].append(topic)
        
        interaction_data['ai_interactions'] = ai_interactions
        session.interaction_data = interaction_data
        
        db.session.commit()
        
        return jsonify({
            'message': 'AI interaction tracked',
            'session': session.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@tracking_bp.route('/session/<int:session_id>/video-engagement', methods=['POST'])
@jwt_required()
def track_video_engagement(session_id):
    """记录视频观看数据"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        session = LearningSession.query.filter_by(
            id=session_id,
            user_id=user_id
        ).first()
        
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # 更新视频观看数据
        video_engagement = session.video_engagement or {
            'playback_events': [],
            'watch_segments': [],
            'interaction_heatmap': {}
        }
        
        # 添加播放事件
        if data.get('playback_event'):
            if 'playback_events' not in video_engagement:
                video_engagement['playback_events'] = []
            video_engagement['playback_events'].append(data['playback_event'])
        
        # 更新观看片段
        if data.get('watch_segment'):
            if 'watch_segments' not in video_engagement:
                video_engagement['watch_segments'] = []
            video_engagement['watch_segments'].append(data['watch_segment'])
        
        session.video_engagement = video_engagement
        db.session.commit()
        
        return jsonify({
            'message': 'Video engagement tracked',
            'session': session.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@tracking_bp.route('/session/<int:session_id>/exercise-attempt', methods=['POST'])
@jwt_required()
def track_exercise_attempt(session_id):
    """记录练习题尝试"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        session = LearningSession.query.filter_by(
            id=session_id,
            user_id=user_id
        ).first()
        
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # 更新练习数据
        interaction_data = session.interaction_data or {}
        exercise_attempts = interaction_data.get('exercise_attempts', {
            'total_attempts': 0,
            'correct_count': 0,
            'time_spent_seconds': 0,
            'attempts': []
        })
        
        exercise_attempts['total_attempts'] = exercise_attempts.get('total_attempts', 0) + 1
        
        if data.get('is_correct'):
            exercise_attempts['correct_count'] = exercise_attempts.get('correct_count', 0) + 1
        
        exercise_attempts['time_spent_seconds'] = exercise_attempts.get('time_spent_seconds', 0) + \
            data.get('time_spent', 0)
        
        # 记录具体尝试
        if 'attempts' not in exercise_attempts:
            exercise_attempts['attempts'] = []
        
        exercise_attempts['attempts'].append({
            'exercise_id': data.get('exercise_id'),
            'is_correct': data.get('is_correct'),
            'time_spent': data.get('time_spent'),
            'timestamp': datetime.utcnow().isoformat()
        })
        
        interaction_data['exercise_attempts'] = exercise_attempts
        session.interaction_data = interaction_data
        
        db.session.commit()
        
        return jsonify({
            'message': 'Exercise attempt tracked',
            'session': session.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@tracking_bp.route('/session/<int:session_id>', methods=['GET'])
@jwt_required()
def get_session(session_id):
    """获取会话详情"""
    try:
        user_id = get_jwt_identity()
        
        session = LearningSession.query.filter_by(
            id=session_id,
            user_id=user_id
        ).first()
        
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        return jsonify({
            'session': session.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@tracking_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_user_sessions():
    """获取用户的所有会话"""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        sessions = LearningSession.query.filter_by(
            user_id=user_id
        ).order_by(LearningSession.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'sessions': [s.to_dict() for s in sessions.items],
            'total': sessions.total,
            'pages': sessions.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@tracking_bp.route('/cleanup/expired', methods=['POST'])
def cleanup_expired_data():
    """清理过期数据（定时任务调用）"""
    try:
        now = datetime.utcnow()
        
        # 删除过期的会话
        expired_sessions = LearningSession.query.filter(
            LearningSession.should_delete_after <= now
        ).all()
        
        session_count = len(expired_sessions)
        
        for session in expired_sessions:
            # 删除关联的事件
            InteractionEvent.query.filter_by(session_id=session.id).delete()
            db.session.delete(session)
        
        # 删除过期的独立事件
        expired_events = InteractionEvent.query.filter(
            InteractionEvent.should_delete_after <= now
        ).delete()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Cleanup completed',
            'sessions_deleted': session_count,
            'events_deleted': expired_events
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
