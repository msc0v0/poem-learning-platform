from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, LearningRecord, UserExerciseRecord, QARecord, Poem, Exercise, LearningSession, InteractionEvent
from datetime import datetime, timedelta
import json

dashboard_bp = Blueprint('dashboard', __name__)


def _safe_list(value):
    return value if isinstance(value, list) else []


def _safe_dict(value):
    return value if isinstance(value, dict) else {}


def _build_learning_report(user_id):
    sessions = LearningSession.query.filter_by(user_id=user_id, is_completed=True)\
        .order_by(LearningSession.start_time.desc()).limit(10).all()

    if not sessions:
        return {
            'summary': {
                'study_style': '探索型学习者',
                'engagement_score': 0,
                'focus_score': 0,
                'preferred_modality': '待识别',
                'consistency_score': 0
            },
            'metrics': {
                'completed_sessions': 0,
                'average_session_minutes': 0,
                'average_ai_interactions': 0,
                'average_video_completion': 0,
                'average_mouse_movements': 0
            },
            'radar': {
                'engagement': 0,
                'focus': 0,
                'consistency': 0,
                'expression': 0
            },
            'strengths': ['开始一次完整学习后，这里会生成你的行为分析报告。'],
            'suggestions': ['先完成一首诗的学习、视频观看和一次 AI 提问，系统就能给出个性化建议。'],
            'recent_report': None
        }

    completed_sessions = len(sessions)
    avg_duration = sum((session.duration_seconds or 0) for session in sessions) / completed_sessions
    avg_quality = sum((session.completion_quality or 0) for session in sessions) / completed_sessions

    total_ai = 0
    total_video_completion = 0
    counted_videos = 0
    total_mouse_movements = 0
    total_clicks = 0
    total_audio_practice = 0
    video_sessions = 0
    ai_sessions = 0
    audio_sessions = 0
    hover_totals = {}

    for session in sessions:
        text_interactions = _safe_list(session.text_interactions)
        total_ai += len(text_interactions)
        if text_interactions:
            ai_sessions += 1

        video_engagement = _safe_dict(session.video_engagement)
        for _, video_data in video_engagement.items():
            if isinstance(video_data, dict) and 'completionRate' in video_data:
                total_video_completion += video_data.get('completionRate', 0)
                counted_videos += 1
                video_sessions += 1

        attention_tracking = _safe_dict(session.attention_tracking)
        mouse_movements = _safe_list(attention_tracking.get('mouseMovements'))
        clicks = _safe_list(attention_tracking.get('clicks'))
        total_mouse_movements += len(mouse_movements)
        total_clicks += len(clicks)

        hover_areas = _safe_dict(attention_tracking.get('hoverAreas'))
        for area, value in hover_areas.items():
            hover_totals[area] = hover_totals.get(area, 0) + (value or 0)

        interaction_data = _safe_dict(session.interaction_data)
        audio_data = _safe_dict(interaction_data.get('audioData'))
        pronunciation_practice = _safe_list(audio_data.get('pronunciationPractice'))
        total_audio_practice += len(pronunciation_practice)
        if pronunciation_practice:
            audio_sessions += 1

    avg_ai = total_ai / completed_sessions
    avg_video_completion = (total_video_completion / counted_videos) if counted_videos else 0
    avg_mouse_movements = total_mouse_movements / completed_sessions
    engagement_score = round(avg_quality * 100, 1)
    focus_score = round(min(100, (avg_mouse_movements * 0.8) + (total_clicks / completed_sessions * 2)), 1)
    expression_score = round(min(100, (avg_ai * 20) + (audio_sessions / completed_sessions * 35) + (total_audio_practice * 8)), 1)

    modality_scores = {
        '视频理解': video_sessions,
        'AI探究': ai_sessions,
        '发音练习': audio_sessions
    }
    preferred_modality = max(modality_scores, key=modality_scores.get) if any(modality_scores.values()) else '综合学习'

    active_days = db.session.query(
        db.func.count(db.distinct(db.func.date(LearningSession.start_time)))
    ).filter(
        LearningSession.user_id == user_id,
        LearningSession.is_completed == True,
        LearningSession.start_time >= datetime.utcnow() - timedelta(days=14)
    ).scalar() or 0
    consistency_score = round(min(100, active_days / 14 * 100), 1)

    dominant_hover_area = max(hover_totals, key=hover_totals.get) if hover_totals else None
    study_style = '平衡型学习者'
    if preferred_modality == 'AI探究':
        study_style = '探究型学习者'
    elif preferred_modality == '视频理解':
        study_style = '视觉型学习者'
    elif preferred_modality == '发音练习':
        study_style = '表达型学习者'

    strengths = []
    suggestions = []

    if avg_ai >= 1:
        strengths.append('你愿意主动向 AI 提问，说明具备较强的探究意识。')
    if avg_video_completion >= 0.5:
        strengths.append('你对视频内容保持了较好的持续观看，适合通过意象视频加深理解。')
    if total_audio_practice > 0:
        strengths.append('你已经参与发音练习，口语输出意识较好。')
    if consistency_score >= 40:
        strengths.append('最近两周学习较稳定，已经形成一定节奏。')

    if not strengths:
        strengths.append('你已经开始形成自己的古诗学习路径。')

    if avg_video_completion < 0.4:
        suggestions.append('建议完整观看至少一段意象视频，再回到诗句理解，能明显提升意境把握。')
    if avg_ai < 1:
        suggestions.append('每次学习后尝试向 AI 提一个问题，例如“这首诗表达了什么情感？”。')
    if total_audio_practice == 0:
        suggestions.append('建议增加发音练习，朗读能帮助记忆节奏和情感。')
    if consistency_score < 30:
        suggestions.append('建议把学习拆成 5-10 分钟的小任务，保持更稳定的学习频率。')

    if not suggestions:
        suggestions.append('继续保持当前节奏，可以开始挑战更高难度或跨朝代的诗歌。')

    latest_session = sessions[0]
    latest_poem = Poem.query.get(latest_session.poem_id)

    return {
        'summary': {
            'study_style': study_style,
            'engagement_score': engagement_score,
            'focus_score': focus_score,
            'preferred_modality': preferred_modality,
            'consistency_score': consistency_score,
            'dominant_area': dominant_hover_area
        },
        'metrics': {
            'completed_sessions': completed_sessions,
            'average_session_minutes': round(avg_duration / 60, 1),
            'average_ai_interactions': round(avg_ai, 1),
            'average_video_completion': round(avg_video_completion * 100, 1),
            'average_mouse_movements': round(avg_mouse_movements, 1)
        },
        'radar': {
            'engagement': engagement_score,
            'focus': focus_score,
            'consistency': consistency_score,
            'expression': expression_score
        },
        'strengths': strengths[:3],
        'suggestions': suggestions[:3],
        'recent_report': {
            'poem_title': latest_poem.title if latest_poem else '未知诗歌',
            'duration_seconds': latest_session.duration_seconds or 0,
            'completion_quality': round((latest_session.completion_quality or 0) * 100, 1)
        }
    }


@dashboard_bp.route('/learning-report', methods=['GET'])
@jwt_required()
def get_learning_report():
    """获取学习行为分析报告"""
    try:
        user_id = get_jwt_identity()
        report = _build_learning_report(user_id)
        return jsonify(report), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/overview', methods=['GET'])
@jwt_required()
def get_dashboard_overview():
    """获取仪表板概览数据"""
    try:
        user_id = get_jwt_identity()
        
        # 用户基本信息
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # 学习统计
        total_poems_accessed = LearningRecord.query.filter_by(user_id=user_id).count()
        completed_poems = LearningRecord.query.filter_by(
            user_id=user_id, is_completed=True
        ).count()
        
        # 练习统计
        total_exercises = UserExerciseRecord.query.filter_by(user_id=user_id).count()
        correct_exercises = UserExerciseRecord.query.filter_by(
            user_id=user_id, is_correct=True
        ).count()
        
        # AI问答统计
        total_questions = QARecord.query.filter_by(user_id=user_id).count()
        
        # 总学习时间
        total_time_result = db.session.query(
            db.func.sum(LearningRecord.reading_time + 
                       LearningRecord.video_watch_time + 
                       LearningRecord.audio_listen_time)
        ).filter_by(user_id=user_id).scalar()
        
        total_study_time = (total_time_result or 0) // 60  # 转换为分钟
        
        # 最近活动
        recent_activity = []
        
        # 最近的学习记录
        recent_learning = LearningRecord.query.filter_by(user_id=user_id)\
            .order_by(LearningRecord.last_visit.desc()).limit(5).all()
        
        for record in recent_learning:
            poem = Poem.query.get(record.poem_id)
            if poem:
                recent_activity.append({
                    'type': 'learning',
                    'title': f'学习了《{poem.title}》',
                    'time': record.last_visit.isoformat(),
                    'poem_id': poem.id
                })
        
        # 最近的练习记录
        recent_exercises = UserExerciseRecord.query.filter_by(user_id=user_id)\
            .order_by(UserExerciseRecord.answered_at.desc()).limit(3).all()
        
        for record in recent_exercises:
            exercise = Exercise.query.get(record.exercise_id)
            if exercise:
                poem = Poem.query.get(exercise.poem_id)
                if poem:
                    recent_activity.append({
                        'type': 'exercise',
                        'title': f'完成了《{poem.title}》的{exercise.question_type}练习',
                        'time': record.answered_at.isoformat(),
                        'is_correct': record.is_correct
                    })
        
        # 按时间排序
        recent_activity.sort(key=lambda x: x['time'], reverse=True)
        recent_activity = recent_activity[:10]  # 只保留最近10条
        
        return jsonify({
            'user_info': user.to_dict(),
            'statistics': {
                'total_poems_accessed': total_poems_accessed,
                'completed_poems': completed_poems,
                'completion_rate': (completed_poems / total_poems_accessed * 100) if total_poems_accessed > 0 else 0,
                'total_exercises': total_exercises,
                'exercise_accuracy': (correct_exercises / total_exercises * 100) if total_exercises > 0 else 0,
                'total_questions': total_questions,
                'total_study_time_minutes': total_study_time
            },
            'recent_activity': recent_activity
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/learning-trends', methods=['GET'])
@jwt_required()
def get_learning_trends():
    """获取学习趋势数据"""
    try:
        user_id = get_jwt_identity()
        days = request.args.get('days', 30, type=int)
        
        today = datetime.utcnow().date()
        start_day = today - timedelta(days=days - 1)
        
        # 按日期统计学习数据
        daily_data = []
        current_day = start_day
        
        while current_day <= today:
            day_start = datetime.combine(current_day, datetime.min.time())
            next_day_start = day_start + timedelta(days=1)
            
            # 当天的学习时间
            day_time_result = db.session.query(
                db.func.sum(LearningRecord.reading_time + 
                           LearningRecord.video_watch_time + 
                           LearningRecord.audio_listen_time)
            ).filter(
                LearningRecord.user_id == user_id,
                LearningRecord.last_visit >= day_start,
                LearningRecord.last_visit < next_day_start
            ).scalar()
            
            study_time = (day_time_result or 0) // 60  # 转换为分钟
            
            # 当天学习的诗歌数量
            poems_count = db.session.query(
                db.func.count(db.distinct(LearningRecord.poem_id))
            ).filter(
                LearningRecord.user_id == user_id,
                LearningRecord.last_visit >= day_start,
                LearningRecord.last_visit < next_day_start
            ).scalar()
            
            # 当天完成的练习数量
            exercises_count = UserExerciseRecord.query.filter(
                UserExerciseRecord.user_id == user_id,
                UserExerciseRecord.answered_at >= day_start,
                UserExerciseRecord.answered_at < next_day_start
            ).count()
            
            daily_data.append({
                'date': current_day.strftime('%Y-%m-%d'),
                'study_time_minutes': study_time,
                'poems_studied': poems_count,
                'exercises_completed': exercises_count
            })
            
            current_day = current_day + timedelta(days=1)
        
        return jsonify({'learning_trends': daily_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/performance-analysis', methods=['GET'])
@jwt_required()
def get_performance_analysis():
    """获取学习表现分析"""
    try:
        user_id = get_jwt_identity()
        
        # 各题型表现
        type_performance = db.session.query(
            Exercise.question_type,
            db.func.count(UserExerciseRecord.id).label('total'),
            db.func.sum(db.case((UserExerciseRecord.is_correct == True, 1), else_=0)).label('correct'),
            db.func.avg(UserExerciseRecord.time_spent).label('avg_time')
        ).join(UserExerciseRecord, UserExerciseRecord.exercise_id == Exercise.id).filter(
            UserExerciseRecord.user_id == user_id
        ).group_by(Exercise.question_type).all()
        
        performance_data = []
        for perf in type_performance:
            performance_data.append({
                'question_type': perf.question_type,
                'total_attempts': perf.total,
                'correct_answers': perf.correct,
                'accuracy_rate': (perf.correct / perf.total * 100) if perf.total > 0 else 0,
                'average_time_seconds': perf.avg_time or 0
            })
        
        # 难度级别表现
        difficulty_performance = db.session.query(
            Poem.difficulty_level,
            db.func.count(LearningRecord.id).label('accessed'),
            db.func.sum(db.case((LearningRecord.is_completed == True, 1), else_=0)).label('completed')
        ).join(LearningRecord, LearningRecord.poem_id == Poem.id).filter(
            LearningRecord.user_id == user_id
        ).group_by(Poem.difficulty_level).all()
        
        difficulty_data = []
        for diff in difficulty_performance:
            difficulty_data.append({
                'difficulty_level': diff.difficulty_level,
                'poems_accessed': diff.accessed,
                'poems_completed': diff.completed,
                'completion_rate': (diff.completed / diff.accessed * 100) if diff.accessed > 0 else 0
            })
        
        # 学习偏好分析
        dynasty_preference = db.session.query(
            Poem.dynasty,
            db.func.count(LearningRecord.id).label('count'),
            db.func.avg(LearningRecord.reading_time + 
                       LearningRecord.video_watch_time + 
                       LearningRecord.audio_listen_time).label('avg_time')
        ).join(LearningRecord, LearningRecord.poem_id == Poem.id).filter(
            LearningRecord.user_id == user_id
        ).group_by(Poem.dynasty).all()
        
        preference_data = []
        for pref in dynasty_preference:
            preference_data.append({
                'dynasty': pref.dynasty,
                'poems_studied': pref.count,
                'average_study_time_seconds': pref.avg_time or 0
            })
        
        return jsonify({
            'type_performance': performance_data,
            'difficulty_performance': difficulty_data,
            'dynasty_preference': preference_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_learning_recommendations():
    """获取个性化学习推荐"""
    try:
        user_id = get_jwt_identity()
        
        # 分析用户学习模式
        user_records = LearningRecord.query.filter_by(user_id=user_id).all()
        learning_report = _build_learning_report(user_id)
        
        if not user_records:
            return jsonify({
                'recommendations': [],
                'message': '开始学习古诗来获得个性化推荐！'
            }), 200
        
        # 计算用户偏好
        dynasty_counts = {}
        difficulty_counts = {}
        total_study_time = 0
        
        for record in user_records:
            poem = Poem.query.get(record.poem_id)
            if poem:
                dynasty_counts[poem.dynasty] = dynasty_counts.get(poem.dynasty, 0) + 1
                difficulty_counts[poem.difficulty_level] = difficulty_counts.get(poem.difficulty_level, 0) + 1
                total_study_time += (record.reading_time + record.video_watch_time + record.audio_listen_time)
        
        # 找出偏好的朝代
        favorite_dynasty = max(dynasty_counts, key=dynasty_counts.get) if dynasty_counts else None
        
        # 找出适合的难度级别
        avg_difficulty = sum(d * c for d, c in difficulty_counts.items()) / sum(difficulty_counts.values()) if difficulty_counts else 1
        recommended_difficulty = min(5, max(1, round(avg_difficulty + 0.5)))  # 稍微提高难度
        
        # 获取已学习的诗歌ID
        learned_poem_ids = [record.poem_id for record in user_records]
        
        recommendations = []

        if learning_report['summary']['preferred_modality'] == 'AI探究':
            recommendations.append({
                'poem': None,
                'reason': '你偏好通过提问理解诗歌，建议优先学习带有丰富背景和赏析信息的作品。',
                'type': 'study_tip',
                'title': '学习策略建议',
                'description': '先读背景，再向 AI 连续提 2-3 个问题，最后完成练习巩固。'
            })
        elif learning_report['summary']['preferred_modality'] == '视频理解':
            recommendations.append({
                'poem': None,
                'reason': '你更适合借助视觉材料理解诗意。',
                'type': 'study_tip',
                'title': '学习策略建议',
                'description': '优先选择带视频资源的诗歌，先看视频再精读诗句。'
            })
        elif learning_report['summary']['preferred_modality'] == '发音练习':
            recommendations.append({
                'poem': None,
                'reason': '你在朗读和输出型任务中更活跃。',
                'type': 'study_tip',
                'title': '学习策略建议',
                'description': '每首诗先听标准音频，再做 1 次跟读和 1 次自我录音。'
            })
        
        # 推荐1: 相同朝代的诗歌
        if favorite_dynasty:
            similar_poems = Poem.query.filter(
                Poem.dynasty == favorite_dynasty,
                ~Poem.id.in_(learned_poem_ids)
            ).limit(3).all()
            
            for poem in similar_poems:
                recommendations.append({
                    'poem': poem.to_dict(),
                    'reason': f'基于您对{favorite_dynasty}诗歌的偏好推荐',
                    'type': 'dynasty_preference'
                })
        
        # 推荐2: 适合难度的诗歌
        difficulty_poems = Poem.query.filter(
            Poem.difficulty_level == recommended_difficulty,
            ~Poem.id.in_(learned_poem_ids)
        ).limit(2).all()
        
        for poem in difficulty_poems:
            recommendations.append({
                'poem': poem.to_dict(),
                'reason': f'适合您当前水平的难度{recommended_difficulty}级诗歌',
                'type': 'difficulty_match'
            })
        
        # 推荐3: 热门诗歌
        popular_poems = db.session.query(
            Poem,
            db.func.count(LearningRecord.id).label('popularity')
        ).join(LearningRecord).filter(
            ~Poem.id.in_(learned_poem_ids)
        ).group_by(Poem.id).order_by(db.desc('popularity')).limit(2).all()
        
        for poem_tuple in popular_poems:
            poem = poem_tuple[0]
            recommendations.append({
                'poem': poem.to_dict(),
                'reason': '热门诗歌，深受学习者喜爱',
                'type': 'popular'
            })
        
        # 限制推荐数量
        recommendations = recommendations[:6]
        
        return jsonify({
            'recommendations': recommendations,
            'user_preferences': {
                'favorite_dynasty': favorite_dynasty,
                'recommended_difficulty': recommended_difficulty,
                'total_study_time_minutes': total_study_time // 60,
                'preferred_modality': learning_report['summary']['preferred_modality'],
                'study_style': learning_report['summary']['study_style']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/achievements', methods=['GET'])
@jwt_required()
def get_achievements():
    """获取学习成就"""
    try:
        user_id = get_jwt_identity()
        
        # 计算各种成就
        achievements = []
        
        # 学习天数成就
        learning_days = db.session.query(
            db.func.count(db.distinct(db.func.date(LearningRecord.last_visit)))
        ).filter_by(user_id=user_id).scalar()
        
        if learning_days >= 1:
            achievements.append({
                'title': '初学者',
                'description': '开始古诗学习之旅',
                'icon': '🌱',
                'unlocked': True,
                'progress': 100
            })
        
        if learning_days >= 7:
            achievements.append({
                'title': '坚持一周',
                'description': '连续学习7天',
                'icon': '📚',
                'unlocked': True,
                'progress': 100
            })
        
        if learning_days >= 30:
            achievements.append({
                'title': '月度学者',
                'description': '学习满30天',
                'icon': '🎓',
                'unlocked': True,
                'progress': 100
            })
        else:
            achievements.append({
                'title': '月度学者',
                'description': '学习满30天',
                'icon': '🎓',
                'unlocked': False,
                'progress': (learning_days / 30 * 100)
            })
        
        # 诗歌数量成就
        completed_poems = LearningRecord.query.filter_by(
            user_id=user_id, is_completed=True
        ).count()
        
        if completed_poems >= 5:
            achievements.append({
                'title': '诗歌爱好者',
                'description': '完成学习5首古诗',
                'icon': '📖',
                'unlocked': True,
                'progress': 100
            })
        else:
            achievements.append({
                'title': '诗歌爱好者',
                'description': '完成学习5首古诗',
                'icon': '📖',
                'unlocked': False,
                'progress': (completed_poems / 5 * 100)
            })
        
        if completed_poems >= 20:
            achievements.append({
                'title': '古诗达人',
                'description': '完成学习20首古诗',
                'icon': '🏆',
                'unlocked': True,
                'progress': 100
            })
        else:
            achievements.append({
                'title': '古诗达人',
                'description': '完成学习20首古诗',
                'icon': '🏆',
                'unlocked': False,
                'progress': (completed_poems / 20 * 100)
            })
        
        # 练习成就
        correct_exercises = UserExerciseRecord.query.filter_by(
            user_id=user_id, is_correct=True
        ).count()
        
        if correct_exercises >= 10:
            achievements.append({
                'title': '练习新手',
                'description': '正确回答10道练习题',
                'icon': '✅',
                'unlocked': True,
                'progress': 100
            })
        else:
            achievements.append({
                'title': '练习新手',
                'description': '正确回答10道练习题',
                'icon': '✅',
                'unlocked': False,
                'progress': (correct_exercises / 10 * 100)
            })
        
        return jsonify({'achievements': achievements}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
