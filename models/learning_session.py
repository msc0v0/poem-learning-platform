from datetime import datetime
from models import db

class LearningSession(db.Model):
    """学习会话 - 每次打开学习页面就是一个会话"""
    __tablename__ = 'learning_session'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    poem_id = db.Column(db.Integer, db.ForeignKey('poems.id'), nullable=False)
    
    # 基础信息
    start_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_time = db.Column(db.DateTime)
    duration_seconds = db.Column(db.Integer, default=0)
    
    # 设备信息
    device_info = db.Column(db.JSON)  # {device_type, browser, os, screen_size}
    
    # 学习行为数据（JSON）
    interaction_data = db.Column(db.JSON)  # 详细的交互数据
    
    # 多模态数据
    text_interactions = db.Column(db.JSON)  # 文本交互
    video_engagement = db.Column(db.JSON)   # 视频观看数据
    attention_tracking = db.Column(db.JSON) # 注意力追踪
    
    # 摄像头数据（预留）
    camera_data = db.Column(db.JSON)  # {enabled, video_urls, analysis_results}
    
    # 状态
    is_completed = db.Column(db.Boolean, default=False)
    completion_quality = db.Column(db.Float)  # 0-1 完成质量评分
    
    # 数据保留（3天测试期）
    retention_days = db.Column(db.Integer, default=3)
    should_delete_after = db.Column(db.DateTime)  # 自动删除时间
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref=db.backref('learning_sessions', lazy='dynamic'))
    poem = db.relationship('Poem', backref=db.backref('learning_sessions', lazy='dynamic'))
    
    def __init__(self, **kwargs):
        super(LearningSession, self).__init__(**kwargs)
        # 设置自动删除时间（3天后）
        from datetime import timedelta
        if not self.should_delete_after:
            # 使用 retention_days 如果有值，否则默认3天
            retention = self.retention_days if self.retention_days is not None else 3
            self.should_delete_after = datetime.utcnow() + timedelta(days=retention)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'poem_id': self.poem_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration_seconds,
            'device_info': self.device_info,
            'interaction_data': self.interaction_data,
            'text_interactions': self.text_interactions,
            'video_engagement': self.video_engagement,
            'attention_tracking': self.attention_tracking,
            'is_completed': self.is_completed,
            'completion_quality': self.completion_quality,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<LearningSession {self.id} - User:{self.user_id} Poem:{self.poem_id}>'


class InteractionEvent(db.Model):
    """细粒度的交互事件记录"""
    __tablename__ = 'interaction_event'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('learning_session.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 事件信息
    event_type = db.Column(db.String(50), nullable=False)  # page_load, click, scroll, ai_question等
    event_target = db.Column(db.String(100))  # 操作对象
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # 事件详情（JSON）
    event_data = db.Column(db.JSON)  # 事件具体数据
    
    # 上下文信息
    page_context = db.Column(db.JSON)  # 页面状态
    screen_position = db.Column(db.JSON)  # {x, y} 鼠标/触摸位置
    
    # 数据保留
    should_delete_after = db.Column(db.DateTime)  # 自动删除时间
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    session = db.relationship('LearningSession', backref=db.backref('events', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('interaction_events', lazy='dynamic'))
    
    def __init__(self, **kwargs):
        super(InteractionEvent, self).__init__(**kwargs)
        # 设置自动删除时间（3天后）
        from datetime import timedelta
        if not self.should_delete_after:
            self.should_delete_after = datetime.utcnow() + timedelta(days=3)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'event_type': self.event_type,
            'event_target': self.event_target,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'event_data': self.event_data,
            'page_context': self.page_context,
            'screen_position': self.screen_position
        }
    
    def __repr__(self):
        return f'<InteractionEvent {self.id} - {self.event_type}>'
