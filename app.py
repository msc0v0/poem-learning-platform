import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入模型和路由
from models import db, bcrypt
from routes.auth import auth_bp
from routes.poems import poems_bp
from routes.learning import learning_bp
from routes.exercises import exercises_bp
from routes.ai_chat import ai_chat_bp
from routes.dashboard import dashboard_bp
from routes.attention import attention_bp
from routes.tracking import tracking_bp
from routes.voice_training import voice_bp
from routes.multimodal_tracking import multimodal_bp

def create_app():
    app = Flask(__name__)
    
    # 配置
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///poem_platform.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 禁用模板缓存（开发环境）
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    
    # JWT配置 - 延长token有效期
    from datetime import timedelta
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)  # token有效期24小时
    
    # 初始化扩展
    db.init_app(app)
    bcrypt.init_app(app)
    jwt = JWTManager(app)
    CORS(app)
    
    # 注册蓝图
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(poems_bp, url_prefix='/api/poems')
    app.register_blueprint(learning_bp, url_prefix='/api/learning')
    app.register_blueprint(exercises_bp, url_prefix='/api/exercises')
    app.register_blueprint(ai_chat_bp, url_prefix='/api/ai')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(attention_bp, url_prefix='/api/attention')
    app.register_blueprint(tracking_bp, url_prefix='/api/tracking')
    app.register_blueprint(voice_bp, url_prefix='/api/voice')
    app.register_blueprint(multimodal_bp)
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    # JWT错误处理
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Invalid token'}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Authorization token is required'}), 401
    
    # 健康检查
    @app.route('/api/health')
    def health_check():
        return jsonify({'status': 'healthy', 'message': 'Poem Platform API is running'})
    
    # 首页 - 直接跳转到古诗列表页面
    @app.route('/')
    def index():
        from flask import redirect
        return redirect('/poems')
    
    # API文档页面
    @app.route('/api-docs')
    def api_docs():
        from flask import render_template
        return render_template('index.html')
    
    # 仪表板页面
    @app.route('/dashboard')
    def dashboard():
        from flask import render_template
        return render_template('dashboard.html')
    
    # 测试页面
    @app.route('/test')
    def test_poems():
        from flask import render_template
        return render_template('index.html')
    
    # 测试多模态追踪器
    @app.route('/test-tracker')
    def test_tracker():
        from flask import render_template
        return render_template('test_tracker.html')
    
    # 古诗列表页面
    @app.route('/poems')
    def poems_list():
        from flask import render_template
        return render_template('poems_list.html')
    
    # 古诗学习页面
    @app.route('/poem/<int:poem_id>')
    def poem_study(poem_id):
        from flask import render_template
        return render_template('poem_study.html')
    
    # 练习题页面
    @app.route('/exercises')
    def exercises_page():
        from flask import render_template
        return render_template('exercises.html')
    
    # 追踪测试页面
    @app.route('/test-tracking')
    def test_tracking_page():
        from flask import render_template
        return render_template('test_tracking.html')
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        # 创建数据库表
        db.create_all()
        print("Database tables created successfully!")
    
    # 启动应用
    app.run(debug=False, host='0.0.0.0', port=5000)
