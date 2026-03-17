from datetime import datetime
from . import db

class Exercise(db.Model):
    __tablename__ = 'exercises'
    
    id = db.Column(db.Integer, primary_key=True)
    poem_id = db.Column(db.Integer, db.ForeignKey('poems.id'), nullable=False)
    
    # 题目信息
    question_type = db.Column(db.String(50), nullable=False)  # 字词释义/意象识别/情感判断/内容理解
    question = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text)  # JSON格式存储选项
    correct_answer = db.Column(db.String(10), nullable=False)
    explanation = db.Column(db.Text)  # 答案解析
    
    # 难度和权重
    difficulty = db.Column(db.Integer, default=1)  # 1-5
    points = db.Column(db.Integer, default=10)     # 分值
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联关系
    user_records = db.relationship('UserExerciseRecord', backref='exercise', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'poem_id': self.poem_id,
            'question_type': self.question_type,
            'question': self.question,
            'options': self.options,
            'correct_answer': self.correct_answer,
            'explanation': self.explanation,
            'difficulty': self.difficulty,
            'points': self.points,
            'created_at': self.created_at.isoformat()
        }

class UserExerciseRecord(db.Model):
    __tablename__ = 'user_exercise_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    
    # 答题记录
    user_answer = db.Column(db.String(10))
    is_correct = db.Column(db.Boolean, default=False)
    score = db.Column(db.Integer, default=0)
    
    # 时间记录
    time_spent = db.Column(db.Integer, default=0)  # 答题用时（秒）
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'exercise_id': self.exercise_id,
            'user_answer': self.user_answer,
            'is_correct': self.is_correct,
            'score': self.score,
            'time_spent': self.time_spent,
            'answered_at': self.answered_at.isoformat()
        }
