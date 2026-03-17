from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, LearningRecord, UserExerciseRecord, QARecord, Poem, Exercise
from datetime import datetime, timedelta
import json

dashboard_bp = Blueprint('dashboard', __name__)

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
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 按日期统计学习数据
        daily_data = []
        current_date = start_date
        
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            
            # 当天的学习时间
            day_time_result = db.session.query(
                db.func.sum(LearningRecord.reading_time + 
                           LearningRecord.video_watch_time + 
                           LearningRecord.audio_listen_time)
            ).filter(
                LearningRecord.user_id == user_id,
                LearningRecord.last_visit >= current_date,
                LearningRecord.last_visit < next_date
            ).scalar()
            
            study_time = (day_time_result or 0) // 60  # 转换为分钟
            
            # 当天学习的诗歌数量
            poems_count = db.session.query(
                db.func.count(db.distinct(LearningRecord.poem_id))
            ).filter(
                LearningRecord.user_id == user_id,
                LearningRecord.last_visit >= current_date,
                LearningRecord.last_visit < next_date
            ).scalar()
            
            # 当天完成的练习数量
            exercises_count = UserExerciseRecord.query.filter(
                UserExerciseRecord.user_id == user_id,
                UserExerciseRecord.answered_at >= current_date,
                UserExerciseRecord.answered_at < next_date
            ).count()
            
            daily_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'study_time_minutes': study_time,
                'poems_studied': poems_count,
                'exercises_completed': exercises_count
            })
            
            current_date = next_date
        
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
            db.func.sum(db.case([(UserExerciseRecord.is_correct == True, 1)], else_=0)).label('correct'),
            db.func.avg(UserExerciseRecord.time_spent).label('avg_time')
        ).join(UserExerciseRecord).filter(
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
            db.func.sum(db.case([(LearningRecord.is_completed == True, 1)], else_=0)).label('completed')
        ).join(LearningRecord).filter(
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
        ).join(LearningRecord).filter(
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
                'total_study_time_minutes': total_study_time // 60
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
