"""
语音训练API路由
"""
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
import asyncio
from datetime import datetime
from models import db
from services.voice_training_service import voice_service

voice_bp = Blueprint('voice', __name__)

# 配置
UPLOAD_FOLDER = 'static/audio/uploads'
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg', 'webm', 'm4a'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@voice_bp.route('/tts/generate', methods=['POST'])
@jwt_required()
def generate_tts():
    """
    生成TTS音频
    
    请求体:
    {
        "text": "床前明月光",
        "voice": "female_standard",  // female_standard, female_gentle, male_standard, male_energetic
        "rate": "normal"              // slow, normal, fast
    }
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('text'):
            return jsonify({'error': 'text is required'}), 400
        
        text = data['text']
        voice = data.get('voice', 'female_standard')
        rate = data.get('rate', 'normal')
        
        # 生成唯一文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        output_path = f"static/audio/tts_{timestamp}.mp3"
        
        # 异步生成TTS
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        audio_path = loop.run_until_complete(
            voice_service.generate_tts_audio(text, voice, rate, output_path)
        )
        loop.close()
        
        # 返回音频URL
        audio_url = f"/{audio_path}"
        
        return jsonify({
            'success': True,
            'audio_url': audio_url,
            'text': text,
            'voice': voice,
            'rate': rate
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@voice_bp.route('/tts/voices', methods=['GET'])
def get_available_voices():
    """获取可用的音色列表"""
    return jsonify({
        'voices': [
            {
                'id': 'female_standard',
                'name': '女声 - 标准',
                'gender': 'female',
                'description': '清晰标准的女声'
            },
            {
                'id': 'male_standard',
                'name': '男声 - 标准',
                'gender': 'male',
                'description': '清晰标准的男声'
            },
            {
                'id': 'male_energetic',
                'name': '男声 - 活力',
                'gender': 'male',
                'description': '充满活力的男声'
            }
        ],
        'rates': [
            {'id': 'slow', 'name': '慢速', 'description': '适合初学者'},
            {'id': 'normal', 'name': '正常', 'description': '正常语速'},
            {'id': 'fast', 'name': '快速', 'description': '适合进阶学习'}
        ]
    }), 200

@voice_bp.route('/asr/upload', methods=['POST'])
@jwt_required()
def upload_audio_for_recognition():
    """
    上传音频进行语音识别
    """
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        file = request.files['audio']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # 保存文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f"user_{timestamp}.{file.filename.rsplit('.', 1)[1].lower()}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # 语音识别
        result = voice_service.transcribe_audio(filepath)
        
        return jsonify({
            'success': True,
            'transcribed_text': result['text'],
            'language': result['language'],
            'audio_path': filepath
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@voice_bp.route('/pronunciation/evaluate', methods=['POST'])
@jwt_required()
def evaluate_pronunciation():
    """
    评估发音质量
    
    请求体:
    - audio: 音频文件
    - reference_text: 参考文本
    """
    try:
        user_id = get_jwt_identity()
        
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        reference_text = request.form.get('reference_text')
        if not reference_text:
            return jsonify({'error': 'reference_text is required'}), 400
        
        file = request.files['audio']
        
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file'}), 400
        
        # 保存音频文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f"eval_{user_id}_{timestamp}.{file.filename.rsplit('.', 1)[1].lower()}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # 发音评估
        evaluation = voice_service.evaluate_pronunciation(filepath, reference_text)
        
        # 可以选择删除音频文件以节省空间
        # os.remove(filepath)
        
        return jsonify({
            'success': True,
            **evaluation
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@voice_bp.route('/challenge/sentence', methods=['POST'])
@jwt_required()
def challenge_sentence():
    """
    单句挑战模式
    
    请求体:
    - audio: 音频文件
    - sentence: 句子文本
    - sentence_index: 句子索引
    """
    try:
        user_id = get_jwt_identity()
        
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        sentence = request.form.get('sentence')
        sentence_index = request.form.get('sentence_index', 0)
        
        if not sentence:
            return jsonify({'error': 'sentence is required'}), 400
        
        file = request.files['audio']
        
        # 保存音频
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f"challenge_{user_id}_{timestamp}.{file.filename.rsplit('.', 1)[1].lower()}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # 评估
        evaluation = voice_service.evaluate_pronunciation(filepath, sentence)
        
        # 判断是否通过（80分以上）
        passed = evaluation['overall_score'] >= 80
        
        return jsonify({
            'success': True,
            'passed': passed,
            'sentence_index': int(sentence_index),
            **evaluation
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@voice_bp.route('/assess-pronunciation', methods=['POST'])
@jwt_required()
def assess_pronunciation():
    """
    评估古诗朗读发音
    
    请求体:
    - audio: 音频文件 (webm/mp3/wav)
    - poem_id: 古诗ID
    - text: 古诗文本
    """
    try:
        user_id = get_jwt_identity()
        
        if 'audio' not in request.files:
            return jsonify({'error': '未提供音频文件'}), 400
        
        poem_id = request.form.get('poem_id')
        text = request.form.get('text')
        
        if not text:
            return jsonify({'error': '未提供参考文本'}), 400
        
        file = request.files['audio']
        
        if file.filename == '':
            return jsonify({'error': '未选择文件'}), 400
        
        # 保存音频文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'webm'
        filename = f"poem_{user_id}_{poem_id}_{timestamp}.{ext}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # 调用发音评估服务
        evaluation = voice_service.evaluate_pronunciation(filepath, text)
        
        # 可选：删除音频文件以节省空间（或保留用于后续分析）
        # os.remove(filepath)
        
        return jsonify({
            'success': True,
            'overall_score': evaluation.get('overall_score', 0),
            'accuracy_score': evaluation.get('accuracy_score', 0),
            'fluency_score': evaluation.get('fluency_score', 0),
            'intonation_score': evaluation.get('intonation_score', 0),
            'word_scores': evaluation.get('word_scores', []),
            'transcribed_text': evaluation.get('transcribed_text', ''),
            'feedback': evaluation.get('feedback', ''),
            'audio_path': filepath
        }), 200
        
    except Exception as e:
        print(f"发音评估错误: {str(e)}")
        return jsonify({'error': f'评估失败: {str(e)}'}), 500
