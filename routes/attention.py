from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, AttentionTracking
import json
from datetime import datetime

attention_bp = Blueprint('attention', __name__)

@attention_bp.route('/track', methods=['POST'])
@jwt_required()
def track_attention():
    """记录用户注意力追踪数据"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('poem_id') or not data.get('session_id'):
            return jsonify({'error': 'poem_id and session_id are required'}), 400
        
        # 查找或创建追踪记录
        tracking = AttentionTracking.query.filter_by(
            user_id=user_id,
            poem_id=data['poem_id'],
            session_id=data['session_id']
        ).first()
        
        if not tracking:
            tracking = AttentionTracking(
                user_id=user_id,
                poem_id=data['poem_id'],
                session_id=data['session_id']
            )
            db.session.add(tracking)
        
        # 更新追踪数据
        if 'mouse_movements' in data:
            tracking.mouse_movements = json.dumps(data['mouse_movements'])
        
        if 'mouse_clicks' in data:
            tracking.mouse_clicks = json.dumps(data['mouse_clicks'])
        
        if 'scroll_events' in data:
            tracking.scroll_events = json.dumps(data['scroll_events'])
        
        if 'hover_areas' in data:
            tracking.hover_areas = json.dumps(data['hover_areas'])
        
        if 'focus_duration' in data:
            tracking.focus_duration = data['focus_duration']
        
        if 'distraction_count' in data:
            tracking.distraction_count = data['distraction_count']
        
        if 'time_on_poem' in data:
            tracking.time_on_poem = data['time_on_poem']
        
        if 'time_on_ai_chat' in data:
            tracking.time_on_ai_chat = data['time_on_ai_chat']
        
        if 'time_on_exercises' in data:
            tracking.time_on_exercises = data['time_on_exercises']
        
        if 'interaction_density' in data:
            tracking.interaction_density = data['interaction_density']
        
        if 'engagement_score' in data:
            tracking.engagement_score = data['engagement_score']
        
        # 更新会话结束时间
        if data.get('session_ended'):
            tracking.session_end = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Attention data tracked successfully',
            'tracking_id': tracking.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@attention_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_attention_statistics():
    """获取用户的注意力统计数据"""
    try:
        user_id = get_jwt_identity()
        poem_id = request.args.get('poem_id', type=int)
        
        query = AttentionTracking.query.filter_by(user_id=user_id)
        
        if poem_id:
            query = query.filter_by(poem_id=poem_id)
        
        trackings = query.all()
        
        if not trackings:
            return jsonify({
                'total_sessions': 0,
                'average_focus_duration': 0,
                'average_engagement_score': 0,
                'total_distractions': 0
            }), 200
        
        # 计算统计数据
        total_sessions = len(trackings)
        avg_focus = sum(t.focus_duration for t in trackings) / total_sessions
        avg_engagement = sum(t.engagement_score for t in trackings) / total_sessions
        total_distractions = sum(t.distraction_count for t in trackings)
        
        return jsonify({
            'total_sessions': total_sessions,
            'average_focus_duration': avg_focus,
            'average_engagement_score': avg_engagement,
            'total_distractions': total_distractions,
            'sessions': [t.to_dict() for t in trackings]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
