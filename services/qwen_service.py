import os
import requests
import json
import time
import re
from typing import Dict, Any, Optional, Tuple

class QwenService:
    def __init__(self):
        self.api_key = os.getenv('QWEN_API_KEY')
        self.api_url = os.getenv('QWEN_API_URL', 'https://api.siliconflow.cn/v1/chat/completions')
        self.model = "Qwen/Qwen2.5-7B-Instruct"
        
        if not self.api_key:
            raise ValueError("QWEN_API_KEY environment variable is required")
        
        # 常见问题库（预设QA库）
        self.common_qa = self._init_common_qa()
        
        # HSK等级词汇和句式控制
        self.hsk_levels = {
            'HSK1': {'max_chars': 50, 'complexity': 'very_simple'},
            'HSK2': {'max_chars': 80, 'complexity': 'simple'},
            'HSK3': {'max_chars': 120, 'complexity': 'moderate'},
            'HSK4': {'max_chars': 200, 'complexity': 'intermediate'},
            'HSK5': {'max_chars': 300, 'complexity': 'advanced'},
            'HSK6': {'max_chars': 500, 'complexity': 'expert'}
        }
    
    def _init_common_qa(self) -> Dict[str, Dict[str, str]]:
        """初始化常见问题库"""
        return {
            # 李白相关
            "李白是谁": {
                "answer": "李白（701-762年）是唐朝最著名的诗人之一，被称为\"诗仙\"。他的诗歌风格豪放浪漫，想象力丰富，是中国古典诗歌的杰出代表。",
                "category": "作者介绍"
            },
            "李白的诗有什么特点": {
                "answer": "李白的诗歌特点：1）想象丰富、浪漫主义；2）语言豪放、气势磅礴；3）常用夸张手法；4）热爱自然、向往自由。",
                "category": "作者风格"
            },
            
            # 杜甫相关
            "杜甫是谁": {
                "answer": "杜甫（712-770年）是唐朝伟大的现实主义诗人，被称为\"诗圣\"。他的诗歌深刻反映了社会现实，语言精练，被誉为\"诗史\"。",
                "category": "作者介绍"
            },
            
            # 王维相关
            "王维是谁": {
                "answer": "王维（701-761年）是唐朝著名诗人和画家，擅长山水田园诗。他的诗歌意境优美、宁静，诗中有画，画中有诗。",
                "category": "作者介绍"
            },
            
            # 孟浩然相关
            "孟浩然是谁": {
                "answer": "孟浩然（689-740年）是唐朝著名的田园诗人。他的诗歌清新自然，多描写山水田园生活，语言平淡而意境深远。",
                "category": "作者介绍"
            },
            
            # 白居易相关
            "白居易是谁": {
                "answer": "白居易（772-846年）是唐朝著名诗人，主张诗歌要通俗易懂，为民所用。他的诗歌语言简单明了，老人和孩子都能理解。",
                "category": "作者介绍"
            },
            
            # 古诗基础知识
            "什么是五言绝句": {
                "answer": "五言绝句是中国古典诗歌的一种形式。每句五个字，全诗四句。格式是：5字×4句=20字。如《静夜思》就是五言绝句。",
                "category": "诗歌形式"
            },
            "什么是七言绝句": {
                "answer": "七言绝句是古诗的一种形式。每句七个字，全诗四句。格式是：7字×4句=28字。",
                "category": "诗歌形式"
            },
            "什么是律诗": {
                "answer": "律诗是格律严谨的古诗形式，全诗八句。分为五言律诗（每句5字）和七言律诗（每句7字）。律诗要求押韵、对仗，格律复杂。",
                "category": "诗歌形式"
            },
            
            # 文化常识
            "什么是意象": {
                "answer": "意象是诗歌中具有象征意义的形象。比如：月亮常象征思乡、梅花象征高洁品格、柳树象征离别。诗人通过意象表达情感。",
                "category": "文学术语"
            },
            "什么是对仗": {
                "answer": "对仗是古诗的一种修辞手法，指两句诗在结构、词性、意义上相互对应。比如：两个黄鹂鸣翠柳，一行白鹭上青天，就是对仗工整的句子。",
                "category": "文学术语"
            }
        }
    
    def detect_language(self, text: str) -> Tuple[str, float]:
        """检测文本语言
        返回: (语言代码, 置信度)
        支持: zh-中文, en-英文, es-西班牙语, fr-法语, de-德语, ja-日语, ko-韩语
        """
        # 简单的语言检测逻辑
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        total_chars = len(text.strip())
        
        if total_chars == 0:
            return 'unknown', 0.0
        
        chinese_ratio = chinese_chars / total_chars
        
        # 如果中文字符超过30%，认为是中文
        if chinese_ratio > 0.3:
            return 'zh', chinese_ratio
        
        # 检测其他语言的常见词
        text_lower = text.lower()
        
        # 英语常见词
        english_words = ['the', 'is', 'are', 'what', 'how', 'why', 'who', 'when', 'where']
        english_count = sum(1 for word in english_words if word in text_lower)
        
        # 西班牙语常见词
        spanish_words = ['qué', 'cómo', 'por qué', 'quién', 'cuándo', 'dónde', 'es', 'son']
        spanish_count = sum(1 for word in spanish_words if word in text_lower)
        
        # 法语常见词
        french_words = ['que', 'qu', 'comment', 'pourquoi', 'qui', 'quand', 'où', 'est', 'sont']
        french_count = sum(1 for word in french_words if word in text_lower)
        
        if english_count >= 2:
            return 'en', 0.8
        elif spanish_count >= 1:
            return 'es', 0.7
        elif french_count >= 1:
            return 'fr', 0.7
        
        # 默认返回英文（国际学生最常用）
        return 'en', 0.5
    
    def translate_text(self, text: str, target_lang: str = 'en') -> Dict[str, Any]:
        """翻译文本到目标语言
        target_lang: en-英语, es-西班牙语, fr-法语, de-德语, ja-日语, ko-韩语
        """
        lang_names = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'ja': 'Japanese',
            'ko': 'Korean'
        }
        
        target_language = lang_names.get(target_lang, 'English')
        
        system_prompt = f"""You are a professional translator. Translate the Chinese text to {target_language}.
Requirements:
1. Preserve the meaning and tone of the original text
2. Use natural {target_language} expressions
3. For poetry-related content, maintain literary quality
4. Only return the translation, no explanations"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
        
        return self._make_request(messages, temperature=0.3, max_tokens=1000)
    
    def search_common_qa(self, question: str) -> Optional[Dict[str, str]]:
        """搜索常见问题库"""
        question_clean = question.strip().replace('？', '').replace('?', '').replace('！', '').replace('!', '')
        
        # 精确匹配
        if question_clean in self.common_qa:
            return self.common_qa[question_clean]
        
        # 模糊匹配
        for key, value in self.common_qa.items():
            if key in question_clean or question_clean in key:
                return value
        
        return None
    
    def _make_request(self, messages: list, temperature: float = 0.7, max_tokens: int = 1000) -> Dict[str, Any]:
        """发送请求到硅基流动API"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        try:
            start_time = time.time()
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'content': result['choices'][0]['message']['content'],
                    'response_time': response_time,
                    'usage': result.get('usage', {})
                }
            else:
                return {
                    'success': False,
                    'error': f"API request failed: {response.status_code} - {response.text}",
                    'response_time': response_time
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': "Request timeout",
                'response_time': 30.0
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Request error: {str(e)}",
                'response_time': 0.0
            }
    
    def analyze_poem_word(self, poem_title: str, poem_content: str, word: str = None) -> Dict[str, Any]:
        """分析古诗中的字词"""
        system_prompt = """你是一位专业的古诗词专家，专门为国际中文学习者提供古诗词字词解析。
请用简洁易懂的语言解释古诗中的字词含义，包括：
1. 字词的基本含义
2. 在诗中的具体含义
3. 相关的文化背景（如适用）
4. 使用例句帮助理解

请用中文回答，语言要简洁明了，适合中文学习者理解。"""
        
        if word:
            # 如果指定了具体字词
            user_prompt = f"""请解析古诗《{poem_title}》中的字词"{word}"。

诗歌全文：
{poem_content}

请详细解释这个字词在诗中的含义。"""
        else:
            # 如果没有指定字词，让AI自动选择并解析关键字词
            user_prompt = f"""请解析古诗《{poem_title}》中的重要字词。

诗歌全文：
{poem_content}

请选择3-5个最关键、最难理解或最有文化内涵的字词，逐一解释它们的含义和在诗中的作用。"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self._make_request(messages, temperature=0.3)
    
    def explain_poem_background(self, poem_title: str, author: str, poem_content: str) -> Dict[str, Any]:
        """解释古诗的创作背景"""
        system_prompt = """你是一位古诗词专家，专门为国际中文学习者介绍古诗的创作背景。
请提供：
1. 诗人的简要介绍
2. 创作时的历史背景
3. 创作动机和情境
4. 诗歌的主要主题

请用中文回答，语言要生动有趣，帮助学习者更好地理解古诗。"""
        
        user_prompt = f"""请介绍古诗《{poem_title}》的创作背景。

作者：{author}
诗歌全文：
{poem_content}

请详细介绍这首诗的创作背景和历史情境。"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self._make_request(messages, temperature=0.5)
    
    def analyze_poem_artistic_conception(self, poem_title: str, author: str, poem_content: str) -> Dict[str, Any]:
        """分析古诗的意境"""
        system_prompt = """你是一位古诗词鉴赏专家，专门为国际中文学习者分析古诗的意境和艺术特色。
请分析：
1. 诗歌描绘的画面和意象
2. 表达的情感和主题
3. 使用的艺术手法
4. 诗歌的美学价值

请用优美的语言描述，帮助学习者感受古诗的艺术魅力。"""
        
        user_prompt = f"""请分析古诗《{poem_title}》的意境和艺术特色。

作者：{author}
诗歌全文：
{poem_content}

请深入分析这首诗的意境、情感和艺术手法。"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self._make_request(messages, temperature=0.6)
    
    def answer_multilingual_question(self, question: str, poem_context: Optional[str] = None, 
                                     hsk_level: str = 'HSK3', user_language: str = None) -> Dict[str, Any]:
        """回答多语言问题，用HSK等级适配的中文回答
        
        Args:
            question: 用户问题（任何语言）
            poem_context: 诗歌上下文
            hsk_level: HSK等级 (HSK1-HSK6)
            user_language: 用户母语代码（用于提供翻译）
        
        Returns:
            {
                'success': bool,
                'answer_chinese': str,  # 中文答案
                'answer_translation': str,  # 翻译（如果需要）
                'question_language': str,  # 检测到的问题语言
                'user_language': str,  # 用户母语
                'common_qa_used': bool,  # 是否使用了预设QA库
                'response_time': float
            }
        """
        start_time = time.time()
        
        # 1. 检测问题语言
        detected_lang, confidence = self.detect_language(question)
        
        # 2. 如果没有指定用户语言，使用检测到的语言
        if not user_language:
            user_language = detected_lang if detected_lang != 'zh' else 'en'
        
        # 3. 先尝试从常见问题库匹配
        common_answer = self.search_common_qa(question)
        common_qa_used = False
        
        if common_answer:
            # 使用预设答案
            chinese_answer = common_answer['answer']
            common_qa_used = True
        else:
            # 4. 如果问题不是中文，先翻译成中文以便AI更好理解
            if detected_lang != 'zh':
                translate_result = self.translate_text(question, target_lang='zh')
                if translate_result['success']:
                    question_in_chinese = translate_result['content']
                else:
                    question_in_chinese = question
            else:
                question_in_chinese = question
            
            # 5. 根据HSK等级生成中文答案
            level_config = self.hsk_levels.get(hsk_level, self.hsk_levels['HSK3'])
            
            system_prompt = f"""你是一位古诗词专家，为国际中文学习者（{hsk_level}水平）答疑解惑。

回答要求：
1. 使用简单、易懂的中文，适合{hsk_level}学习者
2. 每个回答不超过{level_config['max_chars']}个汉字
3. 使用短句，避免复杂的语法结构
4. 解释关键词汇，必要时在括号中标注拼音
5. 回答要准确、有帮助
6. 如果涉及文化背景，简要说明

HSK{hsk_level[-1]}级别特点：
- HSK1-2: 使用最基础的词汇和语法（如：是、有、在、去等）
- HSK3-4: 可以使用中等难度词汇（如：著名、表达、描写等）
- HSK5-6: 可以使用较高级词汇和成语

请直接用中文回答，不要翻译成其他语言。"""
            
            user_prompt = question_in_chinese
            if poem_context:
                user_prompt = f"关于这首古诗：\n{poem_context}\n\n问题：{question_in_chinese}"
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            result = self._make_request(messages, temperature=0.5, max_tokens=level_config['max_chars'] + 100)
            
            if not result['success']:
                return {
                    'success': False,
                    'error': result['error'],
                    'response_time': time.time() - start_time
                }
            
            chinese_answer = result['content']
        
        # 6. 如果用户母语不是中文，生成翻译
        translation = None
        if user_language and user_language != 'zh':
            trans_result = self.translate_text(chinese_answer, target_lang=user_language)
            if trans_result['success']:
                translation = trans_result['content']
        
        return {
            'success': True,
            'answer_chinese': chinese_answer,
            'answer_translation': translation,
            'question_language': detected_lang,
            'user_language': user_language,
            'common_qa_used': common_qa_used,
            'response_time': time.time() - start_time
        }
    
    def answer_general_question(self, question: str, poem_context: Optional[str] = None) -> Dict[str, Any]:
        """回答关于古诗的一般问题"""
        system_prompt = """你是一位古诗词专家，专门为国际中文学习者答疑解惑。
请用简洁明了的语言回答关于古诗词的问题，包括但不限于：
- 古诗词的基础知识
- 诗词格律和形式
- 文学常识
- 文化背景

请确保答案准确、易懂，适合中文学习者的水平。"""
        
        user_prompt = question
        if poem_context:
            user_prompt = f"基于以下古诗内容，请回答问题：\n\n{poem_context}\n\n问题：{question}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self._make_request(messages, temperature=0.7)
    
    def generate_exercise_questions(self, poem_title: str, author: str, poem_content: str, question_type: str) -> Dict[str, Any]:
        """为古诗生成练习题"""
        type_prompts = {
            "主旨理解": "请为这首古诗生成1道主旨理解选择题，考查学生对诗歌中心思想和主题的把握。",
            "字词理解": "请为这首古诗生成1道字词理解选择题，考查学生对诗中关键字词的理解。",
            "意象赏析": "请为这首古诗生成1道意象赏析选择题，考查学生对诗歌意象和艺术手法的理解。"
        }
        
        system_prompt = f"""你是一位古诗词教学专家，请为国际中文学习者生成古诗练习题。
{type_prompts.get(question_type, "请生成相关练习题。")}

题目要求：
1. 难度适中，适合中文学习者
2. 每题必须有4个选项（A/B/C/D）
3. 选项要有一定的迷惑性，但正确答案要明确
4. 提供详细的答案解析，说明为什么选择该答案
5. 必须严格按照JSON格式返回，不要有任何其他文字

JSON格式（必须严格遵守）：
{{
  "questions": [
    {{
      "question": "题目内容（简洁明了）",
      "options": ["A. 选项内容", "B. 选项内容", "C. 选项内容", "D. 选项内容"],
      "correct_answer": "A",
      "explanation": "详细的答案解析，说明为什么选A"
    }}
  ]
}}

注意：
- correct_answer只能是A、B、C、D其中之一
- options数组必须有4个元素
- 每个选项前要加上"A. "、"B. "、"C. "、"D. "前缀"""
        
        user_prompt = f"""请为古诗《{poem_title}》生成{question_type}类型的练习题。

作者：{author}
诗歌全文：
{poem_content}

请生成1道高质量的选择题，严格按照JSON格式返回。"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self._make_request(messages, temperature=0.3, max_tokens=800)
