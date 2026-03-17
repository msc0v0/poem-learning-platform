from datetime import datetime
from . import db

class QARecord(db.Model):
    __tablename__ = 'qa_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    poem_id = db.Column(db.Integer, db.ForeignKey('poems.id'), nullable=True)  # 可能是通用问题
    
    # 问答内容
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50))  # 字词解析/背景介绍/意境赏析/其他
    
    # 质量评估
    user_rating = db.Column(db.Integer)  # 用户对回答的评分 1-5
    is_helpful = db.Column(db.Boolean)   # 是否有帮助
    
    # 时间记录
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    response_time = db.Column(db.Float)  # AI响应时间（秒）
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'poem_id': self.poem_id,
            'question': self.question,
            'answer': self.answer,
            'question_type': self.question_type,
            'user_rating': self.user_rating,
            'is_helpful': self.is_helpful,
            'created_at': self.created_at.isoformat(),
            'response_time': self.response_time
        }
