from datetime import datetime
from . import db

class LearningRecord(db.Model):
    __tablename__ = 'learning_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    poem_id = db.Column(db.Integer, db.ForeignKey('poems.id'), nullable=False)
    
    # 学习行为数据
    reading_time = db.Column(db.Integer, default=0)      # 阅读时长（秒）
    video_watch_time = db.Column(db.Integer, default=0)  # 视频观看时长（秒）
    audio_listen_time = db.Column(db.Integer, default=0) # 音频收听时长（秒）
    
    # 交互数据
    word_queries = db.Column(db.Text)  # JSON格式存储查询的字词
    ai_interactions = db.Column(db.Integer, default=0)  # AI交互次数
    
    # 学习状态
    is_completed = db.Column(db.Boolean, default=False)
    completion_rate = db.Column(db.Float, default=0.0)  # 完成度 (0-1)
    
    # 时间戳
    first_visit = db.Column(db.DateTime, default=datetime.utcnow)
    last_visit = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'poem_id': self.poem_id,
            'reading_time': self.reading_time,
            'video_watch_time': self.video_watch_time,
            'audio_listen_time': self.audio_listen_time,
            'word_queries': self.word_queries,
            'ai_interactions': self.ai_interactions,
            'is_completed': self.is_completed,
            'completion_rate': self.completion_rate,
            'first_visit': self.first_visit.isoformat(),
            'last_visit': self.last_visit.isoformat()
        }
