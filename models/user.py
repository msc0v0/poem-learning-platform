from datetime import datetime
from . import db, bcrypt
from flask_jwt_extended import create_access_token

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # 学习统计
    total_study_time = db.Column(db.Integer, default=0)  # 总学习时长（分钟）
    poems_studied = db.Column(db.Integer, default=0)     # 已学诗歌数量
    
    # 学习者个性化设置
    hsk_level = db.Column(db.String(10), default='HSK3')  # HSK等级 (HSK1-HSK6)
    native_language = db.Column(db.String(10), default='en')  # 母语代码 (en, es, fr, de, ja, ko等)
    
    # 关联关系
    learning_records = db.relationship('LearningRecord', backref='user', lazy=True)
    exercise_records = db.relationship('UserExerciseRecord', backref='user', lazy=True)
    qa_records = db.relationship('QARecord', backref='user', lazy=True)
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def generate_token(self):
        return create_access_token(identity=self.id)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'total_study_time': self.total_study_time,
            'poems_studied': self.poems_studied,
            'hsk_level': self.hsk_level,
            'native_language': self.native_language
        }
