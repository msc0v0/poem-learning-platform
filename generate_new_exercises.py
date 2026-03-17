"""
练习题生成系统 - 使用硅基流动API
支持基础和进阶两种模式，共9种题型
"""
import requests
import json
import sqlite3
from datetime import datetime

class ExerciseGenerator:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://api.siliconflow.cn/v1/chat/completions"
        self.model = "Pro/zai-org/GLM-4.7"  # 使用GLM-4.7，响应更快
        
    def generate_exercises_for_poem(self, poem_id, poem_title, poem_content, poem_translation):
        """为一首诗生成所有类型的练习题"""
        
        # 基础练习题型
        basic_types = [
            "字词释义选择",
            "诗句排序", 
            "情境理解选择"
        ]
        
        # 进阶练习题型
        advanced_types = [
            "重点字词填空",
            "整句填空",
            "开放式问答"
        ]
        
        all_exercises = []
        
        # 生成基础练习（每种2道）
        for ex_type in basic_types:
            exercises = self._generate_by_type(
                poem_title, poem_content, poem_translation, 
                ex_type, difficulty="基础", count=2
            )
            all_exercises.extend(exercises)
        
        # 生成进阶练习（每种2道）
        for ex_type in advanced_types:
            exercises = self._generate_by_type(
                poem_title, poem_content, poem_translation,
                ex_type, difficulty="进阶", count=2
            )
            all_exercises.extend(exercises)
        
        return all_exercises
    
    def _generate_by_type(self, title, content, translation, ex_type, difficulty, count=2):
        """根据题型生成练习题"""
        
        prompt = self._build_prompt(title, content, translation, ex_type, count)
        
        response = self._call_api(prompt)
        exercises = self._parse_response(response, ex_type, difficulty)
        
        return exercises
    
    def _build_prompt(self, title, content, translation, ex_type, count):
        """构建提示词"""
        
        prompts = {
            "字词释义选择": f"""
请为古诗《{title}》生成{count}道"字词释义选择题"。

诗歌内容：
{content}

要求：
1. 选择诗中的重点生词或多义词
2. 提供4个选项（中文释义）
3. 题目格式：在诗句"XXX"中，"X"字的意思是？
4. 选项要有迷惑性，但正确答案要准确

输出JSON格式：
[
  {{
    "question": "题目内容",
    "options": {{"A": "选项A", "B": "选项B", "C": "选项C", "D": "选项D"}},
    "correct_answer": "A",
    "explanation": "答案解析"
  }}
]
""",
            
            "诗句排序": f"""
请为古诗《{title}》生成{count}道"诗句排序题"。

诗歌内容：
{content}

要求：
1. 打乱诗句顺序（全部打乱或部分打乱）
2. 让学生重新排列成正确顺序
3. 题目格式：请将下列诗句按正确顺序排列

输出JSON格式：
[
  {{
    "question": "请将下列诗句按正确顺序排列",
    "options": {{"A": "句子1→句子2→句子3→句子4", "B": "...", "C": "...", "D": "..."}},
    "correct_answer": "B",
    "explanation": "正确顺序是..."
  }}
]
""",
            
            "情境理解选择": f"""
请为古诗《{title}》生成{count}道"情境理解选择题"。

诗歌内容：
{content}

白话翻译：
{translation}

要求：
1. 考查对诗歌情境、场景、意象的理解
2. 题目可以问：诗人看到/听到什么？诗歌描绘的是什么场景？
3. 选项要具体、生动

输出JSON格式：
[
  {{
    "question": "题目内容",
    "options": {{"A": "选项A", "B": "选项B", "C": "选项C", "D": "选项D"}},
    "correct_answer": "C",
    "explanation": "答案解析"
  }}
]
""",
            
            "重点字词填空": f"""
请为古诗《{title}》生成{count}道"重点字词填空题"。

诗歌内容：
{content}

要求：
1. 挖空重点词汇（动词、形容词、名词）
2. 题目格式：请填写诗句中的空缺字词：XXXX___XXX
3. 提供4个选项供选择

输出JSON格式：
[
  {{
    "question": "请填写诗句中的空缺字词：床前明月___",
    "options": {{"A": "光", "B": "辉", "C": "影", "D": "色"}},
    "correct_answer": "A",
    "explanation": "原句是'床前明月光'..."
  }}
]
""",
            
            "整句填空": f"""
请为古诗《{title}》生成{count}道"整句填空题"。

诗歌内容：
{content}

白话翻译：
{translation}

要求：
1. 给出情境提示或英文释义，要求填写完整诗句
2. 提供4个选项（完整诗句）
3. 题目格式：根据提示填写诗句：[情境描述]

输出JSON格式：
[
  {{
    "question": "根据提示填写诗句：诗人抬头看明月的这一句是？",
    "options": {{"A": "举头望明月", "B": "低头思故乡", "C": "床前明月光", "D": "疑是地上霜"}},
    "correct_answer": "A",
    "explanation": "这句描写抬头的动作..."
  }}
]
""",
            
            "开放式问答": f"""
请为古诗《{title}》生成{count}道"开放式问答题"（简答题）。

诗歌内容：
{content}

白话翻译：
{translation}

要求：
1. 问题开放，引导学生思考和表达
2. 问题例如：你喜欢这首诗吗？为什么？这首诗让你想到了什么？
3. 提供参考答案（关键词即可）
4. 这类题目不需要选项，correct_answer填"开放题"

输出JSON格式：
[
  {{
    "question": "你喜欢这首诗吗？请用一两个词说明原因。",
    "options": null,
    "correct_answer": "开放题",
    "explanation": "参考答案：可以从意境优美、情感真挚、语言简洁等角度回答"
  }}
]
"""
        }
        
        return prompts.get(ex_type, "")
    
    def _call_api(self, prompt):
        """调用硅基流动API"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位经验丰富的古诗词教学专家，擅长设计各类练习题。请严格按照JSON格式输出。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(self.api_url, headers=headers, json=data, timeout=60)
                response.raise_for_status()
                result = response.json()
                return result['choices'][0]['message']['content']
            except requests.exceptions.Timeout:
                print(f"  ⏱️ 请求超时，重试 {attempt + 1}/{max_retries}...")
                if attempt == max_retries - 1:
                    print(f"  ❌ API调用失败：超时")
                    return None
            except Exception as e:
                print(f"  ❌ API调用失败: {e}")
                if attempt == max_retries - 1:
                    return None
                print(f"  🔄 重试 {attempt + 1}/{max_retries}...")
        
        return None
    
    def _parse_response(self, response, ex_type, difficulty):
        """解析API返回的JSON"""
        
        if not response:
            return []
        
        try:
            # 提取JSON部分
            start = response.find('[')
            end = response.rfind(']') + 1
            json_str = response[start:end]
            
            exercises_data = json.loads(json_str)
            
            # 转换为标准格式
            exercises = []
            for item in exercises_data:
                exercise = {
                    'question_type': ex_type,
                    'difficulty': difficulty,
                    'question': item['question'],
                    'options': json.dumps(item.get('options'), ensure_ascii=False) if item.get('options') else None,
                    'correct_answer': item['correct_answer'],
                    'explanation': item.get('explanation', ''),
                    'points': 10 if difficulty == '基础' else 15
                }
                exercises.append(exercise)
            
            return exercises
        
        except Exception as e:
            print(f"解析响应失败: {e}")
            print(f"原始响应: {response}")
            return []


def delete_old_exercises():
    """删除旧的练习题"""
    conn = sqlite3.connect('instance/poem_platform.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM exercises')
    old_count = cursor.fetchone()[0]
    
    print(f"准备删除 {old_count} 道旧题目...")
    
    cursor.execute('DELETE FROM user_exercise_records')
    cursor.execute('DELETE FROM exercises')
    conn.commit()
    
    print("✅ 旧题目已删除")
    conn.close()


def generate_all_exercises(api_key):
    """为所有诗歌生成新练习题"""
    
    generator = ExerciseGenerator(api_key)
    conn = sqlite3.connect('instance/poem_platform.db')
    cursor = conn.cursor()
    
    # 获取所有诗歌
    cursor.execute('SELECT id, title, content, translation FROM poems')
    poems = cursor.fetchall()
    
    print(f"\n开始为 {len(poems)} 首诗生成练习题...")
    print("=" * 60)
    
    total_generated = 0
    
    for poem in poems:
        poem_id, title, content, translation = poem
        print(f"\n处理: 《{title}》...")
        
        exercises = generator.generate_exercises_for_poem(
            poem_id, title, content, translation
        )
        
        # 保存到数据库
        for ex in exercises:
            try:
                cursor.execute('''
                    INSERT INTO exercises 
                    (poem_id, question_type, question, options, correct_answer, explanation, difficulty, points)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    poem_id,
                    ex['question_type'],
                    ex['question'],
                    ex['options'],
                    ex['correct_answer'],
                    ex['explanation'],
                    1 if ex['difficulty'] == '基础' else 2,
                    ex['points']
                ))
                total_generated += 1
                print(f"  ✓ {ex['question_type']} ({ex['difficulty']})")
            except Exception as e:
                print(f"  ✗ 保存失败: {e}")
        
        conn.commit()
    
    print("\n" + "=" * 60)
    print(f"✅ 共生成 {total_generated} 道新题目")
    
    conn.close()


if __name__ == '__main__':
    print("古诗词练习题生成系统")
    print("=" * 60)
    print(f"使用模型: Pro/zai-org/GLM-4.7")
    print(f"API提供商: 硅基流动 (siliconflow.cn)")
    
    # 使用预设的API Key
    api_key = "sk-zzyesjjoxlxlfptbpwjnrxvxybunudvbqbaysrddqljqeiqf"
    
    # 确认删除旧题
    print(f"\n⚠️  将删除现有的42道旧题目")
    print(f"📝 为13首诗生成新题目（每首12道，共156道）")
    print(f"\n题型设计：")
    print(f"  [基础] 字词释义选择 × 2")
    print(f"  [基础] 诗句排序 × 2")
    print(f"  [基础] 情境理解选择 × 2")
    print(f"  [进阶] 重点字词填空 × 2")
    print(f"  [进阶] 整句填空 × 2")
    print(f"  [进阶] 开放式问答 × 2")
    
    confirm = input("\n是否继续？(y/n): ").strip().lower()
    
    if confirm != 'y':
        print("已取消操作")
        exit(0)
    
    # 执行
    delete_old_exercises()
    generate_all_exercises(api_key)
    
    print("\n🎉 全部完成！")
    print("\n运行以下命令查看生成结果：")
    print("  python view_new_exercises.py")
