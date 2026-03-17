from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Exercise, UserExerciseRecord, Poem
from services.qwen_service import QwenService
import json

exercises_bp = Blueprint('exercises', __name__)
qwen_service = QwenService()

@exercises_bp.route('/poem/<int:poem_id>', methods=['GET'])
@jwt_required()
def get_poem_exercises(poem_id):
    """获取指定古诗的练习题"""
    try:
        poem = Poem.query.get(poem_id)
        if not poem:
            return jsonify({'error': 'Poem not found'}), 404
        
        question_type = request.args.get('type')
        
        query = Exercise.query.filter_by(poem_id=poem_id)
        if question_type:
            query = query.filter_by(question_type=question_type)
        
        exercises = query.all()
        
        # 构建返回数据（不返回正确答案）
        exercises_data = []
        for exercise in exercises:
            try:
                exercise_dict = {
                    'id': exercise.id,
                    'poem_id': exercise.poem_id,
                    'question_type': exercise.question_type,
                    'question': exercise.question,
                    'difficulty': exercise.difficulty,
                    'points': exercise.points
                }
                
                # 解析选项JSON
                if exercise.options:
                    try:
                        if isinstance(exercise.options, str):
                            exercise_dict['options'] = json.loads(exercise.options)
                        else:
                            exercise_dict['options'] = exercise.options
                    except (json.JSONDecodeError, TypeError) as e:
                        print(f"解析选项失败 (ID={exercise.id}): {e}")
                        exercise_dict['options'] = None
                else:
                    exercise_dict['options'] = None
                
                exercises_data.append(exercise_dict)
            except Exception as e:
                print(f"处理练习题失败 (ID={exercise.id}): {e}")
                continue
        
        return jsonify({
            'exercises': exercises_data,
            'poem': {
                'id': poem.id,
                'title': poem.title,
                'author': poem.author
            }
        }), 200
        
    except Exception as e:
        print(f"获取练习题失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@exercises_bp.route('/generate/<int:poem_id>', methods=['POST'])
@jwt_required()
def generate_exercises(poem_id):
    """为指定古诗生成练习题"""
    try:
        poem = Poem.query.get(poem_id)
        if not poem:
            return jsonify({'error': 'Poem not found'}), 404
        
        data = request.get_json()
        question_type = data.get('question_type', '字词释义')
        
        if question_type not in ['字词释义', '意象识别', '情感判断', '内容理解']:
            return jsonify({'error': 'Invalid question type'}), 400
        
        # 调用AI服务生成题目
        result = qwen_service.generate_exercise_questions(
            poem.title, poem.author, poem.content, question_type
        )
        
        if not result['success']:
            return jsonify({'error': result['error']}), 500
        
        # 解析AI返回的题目
        try:
            questions_data = json.loads(result['content'])
            questions = questions_data.get('questions', [])
        except json.JSONDecodeError:
            return jsonify({'error': 'Failed to parse generated questions'}), 500
        
        # 保存题目到数据库
        created_exercises = []
        for q in questions:
            exercise = Exercise(
                poem_id=poem_id,
                question_type=question_type,
                question=q['question'],
                options=json.dumps(q['options']),
                correct_answer=q['correct_answer'],
                explanation=q.get('explanation', ''),
                difficulty=2,  # 默认难度
                points=10
            )
            db.session.add(exercise)
            created_exercises.append(exercise)
        
        db.session.commit()
        
        # 返回生成的题目（不包含答案）
        exercises_data = []
        for exercise in created_exercises:
            exercise_dict = exercise.to_dict()
            exercise_dict.pop('correct_answer', None)
            exercise_dict.pop('explanation', None)
            exercise_dict['options'] = json.loads(exercise.options)
            exercises_data.append(exercise_dict)
        
        return jsonify({
            'message': f'Generated {len(created_exercises)} exercises',
            'exercises': exercises_data
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@exercises_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_exercise():
    """提交练习答案"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('exercise_id') or not data.get('user_answer'):
            return jsonify({'error': 'exercise_id and user_answer are required'}), 400
        
        exercise = Exercise.query.get(data['exercise_id'])
        if not exercise:
            return jsonify({'error': 'Exercise not found'}), 404
        
        # 检查答案是否正确
        is_correct = data['user_answer'].upper() == exercise.correct_answer.upper()
        score = exercise.points if is_correct else 0
        
        # 保存答题记录
        record = UserExerciseRecord(
            user_id=user_id,
            exercise_id=exercise.id,
            user_answer=data['user_answer'],
            is_correct=is_correct,
            score=score,
            time_spent=data.get('time_spent', 0)
        )
        db.session.add(record)
        db.session.commit()
        
        return jsonify({
            'is_correct': is_correct,
            'score': score,
            'correct_answer': exercise.correct_answer,
            'explanation': exercise.explanation,
            'record_id': record.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@exercises_bp.route('/records', methods=['GET'])
@jwt_required()
def get_exercise_records():
    """获取用户练习记录"""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        poem_id = request.args.get('poem_id', type=int)
        
        query = UserExerciseRecord.query.filter_by(user_id=user_id)
        
        if poem_id:
            # 通过exercise表关联过滤
            query = query.join(Exercise).filter(Exercise.poem_id == poem_id)
        
        records = query.order_by(UserExerciseRecord.answered_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 包含练习题和诗歌信息
        records_with_details = []
        for record in records.items:
            record_dict = record.to_dict()
            exercise = Exercise.query.get(record.exercise_id)
            if exercise:
                record_dict['exercise'] = {
                    'question': exercise.question,
                    'question_type': exercise.question_type,
                    'points': exercise.points
                }
                poem = Poem.query.get(exercise.poem_id)
                if poem:
                    record_dict['poem'] = {
                        'title': poem.title,
                        'author': poem.author
                    }
            records_with_details.append(record_dict)
        
        return jsonify({
            'exercise_records': records_with_details,
            'total': records.total,
            'pages': records.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exercises_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_exercise_statistics():
    """获取练习统计数据"""
    try:
        user_id = get_jwt_identity()
        
        # 总体统计
        total_exercises = UserExerciseRecord.query.filter_by(user_id=user_id).count()
        correct_answers = UserExerciseRecord.query.filter_by(
            user_id=user_id, is_correct=True
        ).count()
        
        total_score = db.session.query(
            db.func.sum(UserExerciseRecord.score)
        ).filter_by(user_id=user_id).scalar() or 0
        
        # 按题型统计
        type_stats = db.session.query(
            Exercise.question_type,
            db.func.count(UserExerciseRecord.id).label('total'),
            db.func.sum(db.case([(UserExerciseRecord.is_correct == True, 1)], else_=0)).label('correct')
        ).join(UserExerciseRecord).filter(
            UserExerciseRecord.user_id == user_id
        ).group_by(Exercise.question_type).all()
        
        type_statistics = {}
        for stat in type_stats:
            type_statistics[stat.question_type] = {
                'total': stat.total,
                'correct': stat.correct,
                'accuracy': (stat.correct / stat.total * 100) if stat.total > 0 else 0
            }
        
        # 平均答题时间
        avg_time = db.session.query(
            db.func.avg(UserExerciseRecord.time_spent)
        ).filter_by(user_id=user_id).scalar() or 0
        
        return jsonify({
            'total_exercises': total_exercises,
            'correct_answers': correct_answers,
            'accuracy_rate': (correct_answers / total_exercises * 100) if total_exercises > 0 else 0,
            'total_score': total_score,
            'average_time_seconds': avg_time,
            'type_statistics': type_statistics
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exercises_bp.route('/types', methods=['GET'])
def get_exercise_types():
    """获取所有练习题类型"""
    return jsonify({
        'exercise_types': [
            {'value': '主旨理解', 'label': '主旨理解', 'description': '考查对古诗中心思想和主题的把握'},
            {'value': '字词理解', 'label': '字词理解', 'description': '考查对古诗中关键字词的理解'},
            {'value': '意象赏析', 'label': '意象赏析', 'description': '考查对诗歌意象和艺术手法的理解'}
        ]
    }), 200

@exercises_bp.route('/batch-generate', methods=['POST'])
@jwt_required()
def batch_generate_exercises():
    """批量生成所有古诗的练习题"""
    try:
        # 获取所有古诗
        poems = Poem.query.all()
        question_types = ['主旨理解', '字词理解', '意象赏析']
        
        generated_count = 0
        failed_poems = []
        
        for poem in poems:
            # 检查是否已有完整题目
            existing = Exercise.query.filter_by(poem_id=poem.id).count()
            if existing >= 3:
                continue
            
            # 为每种类型生成1道题
            for q_type in question_types:
                try:
                    result = qwen_service.generate_exercise_questions(
                        poem.title, poem.author, poem.content, q_type
                    )
                    
                    if not result['success']:
                        failed_poems.append(f"{poem.title} - {q_type}")
                        continue
                    
                    # 解析并保存题目
                    content = result['content'].strip()
                    if content.startswith('```'):
                        content = content.split('\n', 1)[1]
                    if content.endswith('```'):
                        content = content.rsplit('\n', 1)[0]
                    
                    questions_data = json.loads(content)
                    questions = questions_data.get('questions', [])
                    
                    if questions:
                        q = questions[0]
                        exercise = Exercise(
                            poem_id=poem.id,
                            question_type=q_type,
                            question=q['question'],
                            options=json.dumps(q['options'], ensure_ascii=False),
                            correct_answer=q['correct_answer'].upper(),
                            explanation=q['explanation'],
                            difficulty=2,
                            points=10
                        )
                        db.session.add(exercise)
                        generated_count += 1
                    
                except Exception as e:
                    failed_poems.append(f"{poem.title} - {q_type}: {str(e)}")
                    continue
        
        db.session.commit()
        
        return jsonify({
            'message': f'Batch generation completed',
            'generated_count': generated_count,
            'total_poems': len(poems),
            'failed_items': failed_poems
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
