from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from models import db
from models.learning_session import LearningSession, InteractionEvent
from models.attention_tracking import AttentionTracking
from models.learning_record import LearningRecord
import json

multimodal_bp = Blueprint('multimodal_tracking', __name__, url_prefix='/api/tracking/multimodal')


class DataValidator:
    """数据验证和清洗工具类"""
    
    @staticmethod
    def validate_session_data(data):
        """验证会话数据"""
        required_fields = ['sessionId', 'userId', 'poemId', 'sessionData']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        # 验证sessionData结构
        session_data = data['sessionData']
        if not isinstance(session_data, dict):
            return False, "sessionData must be a dictionary"
        
        return True, None
    
    @staticmethod
    def validate_event_data(data):
        """验证事件数据"""
        required_fields = ['sessionId', 'userId', 'events']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        if not isinstance(data['events'], list):
            return False, "events must be a list"
        
        return True, None
    
    @staticmethod
    def clean_mouse_movements(movements):
        """清洗鼠标移动数据 - 去除异常值和采样"""
        if not movements or not isinstance(movements, list):
            return []
        
        cleaned = []
        for move in movements:
            # 验证数据完整性
            if not all(k in move for k in ['x', 'y', 'timestamp']):
                continue
            
            # 验证坐标范围（假设最大屏幕尺寸为4K）
            if not (0 <= move['x'] <= 4096 and 0 <= move['y'] <= 2160):
                continue
            
            # 验证时间戳
            if not isinstance(move['timestamp'], (int, float)):
                continue
            
            cleaned.append(move)
        
        # 如果数据点太多，进行采样（保留最多500个点）
        if len(cleaned) > 500:
            step = len(cleaned) // 500
            cleaned = cleaned[::step]
        
        return cleaned
    
    @staticmethod
    def clean_text_interactions(interactions):
        """清洗文本交互数据"""
        if not interactions or not isinstance(interactions, list):
            return []
        
        cleaned = []
        for interaction in interactions:
            if not isinstance(interaction, dict):
                continue
            
            # 限制文本长度
            if 'question' in interaction:
                interaction['question'] = str(interaction['question'])[:2000]
            if 'answer' in interaction:
                interaction['answer'] = str(interaction['answer'])[:5000]
            
            cleaned.append(interaction)
        
        return cleaned
    
    @staticmethod
    def calculate_engagement_score(session_data):
        """计算参与度评分"""
        score = 0.0
        
        # 视频观看完成度 (0-30分)
        video_engagement = session_data.get('videoEngagement', {})
        for video_type, video_data in video_engagement.items():
            if isinstance(video_data, dict):
                completion_rate = video_data.get('completionRate', 0)
                score += completion_rate * 30
                break  # 只计算一个视频
        
        # AI交互次数 (0-25分)
        text_interactions = session_data.get('textInteractions', [])
        ai_count = len(text_interactions)
        score += min(ai_count * 5, 25)
        
        # 练习完成情况 (0-25分)
        exercise_data = session_data.get('exerciseData', {})
        if isinstance(exercise_data, dict):
            accuracy = exercise_data.get('totalScore', 0) / max(exercise_data.get('completedCount', 1), 1)
            score += accuracy * 25
        
        # 总交互次数 (0-20分)
        trajectory = session_data.get('behaviorTrajectory', [])
        interaction_count = len(trajectory)
        score += min(interaction_count / 10, 20)
        
        return min(score, 100.0)


@multimodal_bp.route('/events', methods=['POST'])
@jwt_required()
def receive_events():
    """接收批量事件数据"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # 数据验证
        is_valid, error_msg = DataValidator.validate_event_data(data)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        session_id = data['sessionId']
        user_id = data.get('userId', current_user_id)
        poem_id = data.get('poemId')
        events = data['events']
        
        # 查找或创建学习会话
        session = LearningSession.query.filter_by(
            user_id=user_id,
            poem_id=poem_id
        ).order_by(LearningSession.start_time.desc()).first()
        
        if not session:
            session = LearningSession(
                user_id=user_id,
                poem_id=poem_id,
                start_time=datetime.utcnow()
            )
            db.session.add(session)
            db.session.flush()
        
        # 批量插入事件
        event_objects = []
        for event in events:
            interaction_event = InteractionEvent(
                session_id=session.id,
                user_id=user_id,
                event_type=event.get('type', 'unknown'),
                event_target=event.get('data', {}).get('target', ''),
                timestamp=datetime.fromtimestamp(event.get('timestamp', 0) / 1000),
                event_data=event.get('data'),
                screen_position={
                    'x': event.get('data', {}).get('x'),
                    'y': event.get('data', {}).get('y')
                } if 'x' in event.get('data', {}) else None
            )
            event_objects.append(interaction_event)
        
        db.session.bulk_save_objects(event_objects)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{len(events)} events received',
            'sessionId': session_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@multimodal_bp.route('/session', methods=['POST'])
def receive_session():
    """接收完整会话数据"""
    try:
        # 支持从 URL 参数或 Header 获取 token（兼容 sendBeacon）
        token = request.args.get('token') or request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if token:
            # 手动验证 JWT token
            from flask_jwt_extended import decode_token
            try:
                decoded = decode_token(token)
                current_user_id = decoded['sub']
            except:
                return jsonify({'error': 'Invalid token'}), 401
        else:
            # 尝试使用标准 JWT 验证
            try:
                from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
                verify_jwt_in_request()
                current_user_id = get_jwt_identity()
            except:
                return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        
        # 数据验证
        is_valid, error_msg = DataValidator.validate_session_data(data)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        session_id_str = data['sessionId']
        user_id = data.get('userId', current_user_id)
        poem_id = data['poemId']
        session_data = data['sessionData']
        
        # 数据清洗
        if 'attentionTracking' in session_data:
            attention = session_data['attentionTracking']
            if 'mouseMovements' in attention:
                attention['mouseMovements'] = DataValidator.clean_mouse_movements(
                    attention['mouseMovements']
                )
        
        if 'textInteractions' in session_data:
            session_data['textInteractions'] = DataValidator.clean_text_interactions(
                session_data['textInteractions']
            )
        
        # 计算参与度评分
        engagement_score = DataValidator.calculate_engagement_score(session_data)
        
        # 查找或创建学习会话
        session = LearningSession.query.filter_by(
            user_id=user_id,
            poem_id=poem_id
        ).order_by(LearningSession.start_time.desc()).first()
        
        if not session:
            session = LearningSession(
                user_id=user_id,
                poem_id=poem_id,
                start_time=datetime.fromisoformat(session_data.get('startTime', datetime.utcnow().isoformat()))
            )
            db.session.add(session)
        
        # 更新会话数据
        session.end_time = datetime.fromisoformat(session_data.get('endTime', datetime.utcnow().isoformat()))
        session.duration_seconds = session_data.get('durationSeconds', 0)
        session.device_info = session_data.get('deviceInfo')
        session.text_interactions = session_data.get('textInteractions')
        session.video_engagement = session_data.get('videoEngagement')
        session.attention_tracking = session_data.get('attentionTracking')
        session.is_completed = True
        session.completion_quality = engagement_score / 100.0
        
        # 更新或创建注意力追踪记录
        attention_data = session_data.get('attentionTracking', {})
        attention_record = AttentionTracking.query.filter_by(
            user_id=user_id,
            poem_id=poem_id,
            session_id=session_id_str
        ).first()
        
        if not attention_record:
            attention_record = AttentionTracking(
                user_id=user_id,
                poem_id=poem_id,
                session_id=session_id_str
            )
            db.session.add(attention_record)
        
        # 更新注意力数据
        attention_record.mouse_movements = json.dumps(attention_data.get('mouseMovements', []))
        attention_record.mouse_clicks = json.dumps(attention_data.get('clicks', []))
        attention_record.scroll_events = json.dumps(attention_data.get('scrolls', []))
        attention_record.hover_areas = json.dumps(attention_data.get('hoverAreas', {}))
        attention_record.engagement_score = engagement_score
        attention_record.session_end = session.end_time
        
        # 计算各区域停留时间
        hover_areas = attention_data.get('hoverAreas', {})
        attention_record.time_on_poem = int(hover_areas.get('poem_content', 0))
        attention_record.time_on_ai_chat = int(hover_areas.get('ai_chat', 0))
        attention_record.time_on_exercises = int(hover_areas.get('exercises', 0))
        
        # 更新学习记录
        learning_record = LearningRecord.query.filter_by(
            user_id=user_id,
            poem_id=poem_id
        ).first()
        
        if not learning_record:
            learning_record = LearningRecord(
                user_id=user_id,
                poem_id=poem_id
            )
            db.session.add(learning_record)
        
        # 更新视频观看时长
        video_engagement = session_data.get('videoEngagement', {})
        total_video_time = 0
        for video_type, video_data in video_engagement.items():
            if isinstance(video_data, dict):
                total_video_time += video_data.get('watchDuration', 0)
        learning_record.video_watch_time = int(total_video_time)
        
        # 更新AI交互次数
        learning_record.ai_interactions = len(session_data.get('textInteractions', []))
        
        # 更新最后访问时间
        learning_record.last_visit = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Session data received and processed',
            'sessionId': session_id_str,
            'engagementScore': engagement_score,
            'dataPoints': {
                'mouseMovements': len(attention_data.get('mouseMovements', [])),
                'clicks': len(attention_data.get('clicks', [])),
                'scrolls': len(attention_data.get('scrolls', [])),
                'textInteractions': len(session_data.get('textInteractions', [])),
                'behaviorEvents': len(session_data.get('behaviorTrajectory', []))
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@multimodal_bp.route('/pronunciation', methods=['POST'])
@jwt_required()
def receive_pronunciation():
    """接收发音评测数据"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        user_id = data.get('userId', current_user_id)
        poem_id = data['poemId']
        scores = data['scores']
        duration = data['duration']
        
        # 查找当前学习会话
        session = LearningSession.query.filter_by(
            user_id=user_id,
            poem_id=poem_id
        ).order_by(LearningSession.start_time.desc()).first()
        
        if session:
            # 更新音频数据
            audio_data = session.text_interactions or {}
            if 'pronunciationPractice' not in audio_data:
                audio_data['pronunciationPractice'] = []
            
            audio_data['pronunciationPractice'].append({
                'timestamp': datetime.utcnow().isoformat(),
                'duration': duration,
                'scores': scores
            })
            
            session.text_interactions = audio_data
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Pronunciation data received'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@multimodal_bp.route('/session/<int:session_id>', methods=['GET'])
@jwt_required()
def get_session_data(session_id):
    """获取会话数据（用于分析）"""
    try:
        current_user_id = get_jwt_identity()
        
        session = LearningSession.query.filter_by(
            id=session_id,
            user_id=current_user_id
        ).first()
        
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        return jsonify({
            'success': True,
            'session': session.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@multimodal_bp.route('/cleanup', methods=['POST'])
def cleanup_old_data():
    """清理过期数据（定时任务调用）"""
    try:
        # 删除过期的学习会话
        expired_sessions = LearningSession.query.filter(
            LearningSession.should_delete_after < datetime.utcnow()
        ).all()
        
        deleted_count = 0
        for session in expired_sessions:
            # 删除关联的事件
            InteractionEvent.query.filter_by(session_id=session.id).delete()
            db.session.delete(session)
            deleted_count += 1
        
        # 删除过期的交互事件
        expired_events = InteractionEvent.query.filter(
            InteractionEvent.should_delete_after < datetime.utcnow()
        ).delete()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Cleaned up {deleted_count} sessions and {expired_events} events'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
