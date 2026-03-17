from datetime import datetime
from . import db

class Poem(db.Model):
    __tablename__ = 'poems'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    dynasty = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    translation = db.Column(db.Text)  # 现代文翻译
    background = db.Column(db.Text)   # 创作背景
    analysis = db.Column(db.Text)     # 诗歌赏析
    english_notes = db.Column(db.Text)  # 英文注释
    
    # 多媒体资源
    video_path = db.Column(db.String(200))  # 意境视频路径
    audio_path = db.Column(db.String(200))  # TTS音频路径
    
    # 字词注释 (JSON格式存储)
    annotations = db.Column(db.Text)  # JSON字符串，格式: {"字词": "注释"}
    
    # 难度等级 (1-5)
    difficulty_level = db.Column(db.Integer, default=1)
    
    # 标签
    tags = db.Column(db.String(200))  # 逗号分隔的标签
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联关系
    learning_records = db.relationship('LearningRecord', backref='poem', lazy=True)
    exercises = db.relationship('Exercise', backref='poem', lazy=True)
    qa_records = db.relationship('QARecord', backref='poem', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'dynasty': self.dynasty,
            'content': self.content,
            'translation': self.translation,
            'background': self.background,
            'analysis': self.analysis,
            'english_notes': self.english_notes,
            'video_path': self.video_path,
            'audio_path': self.audio_path,
            'annotations': self.annotations,
            'difficulty_level': self.difficulty_level,
            'tags': self.tags.split(',') if self.tags else [],
            'created_at': self.created_at.isoformat()
        }
