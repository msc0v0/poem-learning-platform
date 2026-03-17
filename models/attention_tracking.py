from datetime import datetime
from . import db

class AttentionTracking(db.Model):
    """注意力追踪数据模型 - 记录用户的鼠标行为和注意力模式"""
    __tablename__ = 'attention_tracking'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    poem_id = db.Column(db.Integer, db.ForeignKey('poems.id'), nullable=False)
    session_id = db.Column(db.String(100), nullable=False)  # 学习会话ID
    
    # 鼠标行为数据
    mouse_movements = db.Column(db.Text)  # JSON格式：[{x, y, timestamp}, ...]
    mouse_clicks = db.Column(db.Text)     # JSON格式：[{x, y, element, timestamp}, ...]
    scroll_events = db.Column(db.Text)    # JSON格式：[{position, direction, timestamp}, ...]
    
    # 注意力指标
    hover_areas = db.Column(db.Text)      # JSON格式：记录鼠标停留区域
    reading_pattern = db.Column(db.Text)   # JSON格式：阅读模式分析
    focus_duration = db.Column(db.Integer, default=0)  # 专注时长（秒）
    distraction_count = db.Column(db.Integer, default=0)  # 分心次数
    
    # 页面停留时间
    time_on_poem = db.Column(db.Integer, default=0)      # 在古诗区域停留时间
    time_on_ai_chat = db.Column(db.Integer, default=0)   # 在AI对话区域停留时间
    time_on_exercises = db.Column(db.Integer, default=0) # 在练习区域停留时间
    
    # 交互密度
    interaction_density = db.Column(db.Float, default=0.0)  # 交互密度分数
    engagement_score = db.Column(db.Float, default=0.0)     # 参与度评分
    
    # 时间戳
    session_start = db.Column(db.DateTime, default=datetime.utcnow)
    session_end = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'poem_id': self.poem_id,
            'session_id': self.session_id,
            'focus_duration': self.focus_duration,
            'distraction_count': self.distraction_count,
            'time_on_poem': self.time_on_poem,
            'time_on_ai_chat': self.time_on_ai_chat,
            'time_on_exercises': self.time_on_exercises,
            'interaction_density': self.interaction_density,
            'engagement_score': self.engagement_score,
            'session_start': self.session_start.isoformat(),
            'session_end': self.session_end.isoformat() if self.session_end else None,
            'created_at': self.created_at.isoformat()
        }
