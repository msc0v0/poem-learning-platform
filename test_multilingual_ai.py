"""
测试AI智能问答助手的多语言和HSK等级功能
"""
import requests
import json

# 配置
BASE_URL = "http://127.0.0.1:5000"
TOKEN = None  # 需要先登录获取

def login():
    """登录获取token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": "student",
        "password": "student123"
    })
    if response.status_code == 200:
        global TOKEN
        TOKEN = response.json()['token']
        print("✓ 登录成功")
        return True
    else:
        print(f"✗ 登录失败: {response.text}")
        return False

def test_common_questions():
    """测试常见问题库"""
    print("\n" + "="*50)
    print("测试1: 获取常见问题列表")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/api/ai/common-questions")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ 成功获取 {data['total_questions']} 个常见问题")
        print("\n问题分类：")
        for category, questions in data['categories'].items():
            print(f"\n  📁 {category} ({len(questions)}个问题)")
            for q in questions[:2]:  # 只显示前2个
                print(f"     - {q['question']}")
    else:
        print(f"✗ 请求失败: {response.text}")

def test_multilingual_ask(question, hsk_level="HSK3", user_language="en"):
    """测试多语言问答"""
    print("\n" + "="*50)
    print(f"测试: 多语言问答")
    print("="*50)
    print(f"问题: {question}")
    print(f"HSK等级: {hsk_level}")
    print(f"用户母语: {user_language}")
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.post(
        f"{BASE_URL}/api/ai/ask",
        headers=headers,
        json={
            "question": question,
            "hsk_level": hsk_level,
            "user_language": user_language
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ 请求成功 (响应时间: {data['response_time']:.2f}秒)")
        print(f"检测到的问题语言: {data['question_language']}")
        print(f"是否使用预设QA库: {'是' if data['common_qa_used'] else '否'}")
        print(f"\n📖 中文回答:")
        print(f"   {data['answer_chinese']}")
        
        if data['has_translation']:
            print(f"\n🌍 {user_language.upper()} 翻译:")
            print(f"   {data['answer_translation']}")
    else:
        print(f"✗ 请求失败: {response.text}")

def test_update_user_settings():
    """测试更新用户设置"""
    print("\n" + "="*50)
    print("测试: 更新用户HSK等级和母语")
    print("="*50)
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.put(
        f"{BASE_URL}/api/auth/profile",
        headers=headers,
        json={
            "hsk_level": "HSK4",
            "native_language": "es"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        user = data['user']
        print(f"✓ 更新成功")
        print(f"   HSK等级: {user['hsk_level']}")
        print(f"   母语: {user['native_language']}")
    else:
        print(f"✗ 更新失败: {response.text}")

def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*70)
    print("🧪 AI智能问答助手 - 多语言功能测试")
    print("="*70)
    
    # 1. 登录
    if not login():
        print("\n无法继续测试，请检查登录信息")
        return
    
    # 2. 测试常见问题库
    test_common_questions()
    
    # 3. 测试中文提问（预设QA库）
    test_multilingual_ask(
        question="李白是谁",
        hsk_level="HSK3",
        user_language="en"
    )
    
    # 4. 测试英语提问（HSK3）
    test_multilingual_ask(
        question="What does Li Bai write about?",
        hsk_level="HSK3",
        user_language="en"
    )
    
    # 5. 测试西班牙语提问（HSK2）
    test_multilingual_ask(
        question="¿Qué es un poema de cinco caracteres?",
        hsk_level="HSK2",
        user_language="es"
    )
    
    # 6. 测试更新用户设置
    test_update_user_settings()
    
    # 7. 测试不同HSK等级的回答
    print("\n" + "="*50)
    print("测试不同HSK等级的回答差异")
    print("="*50)
    
    question = "什么是意象"
    
    for level in ["HSK1", "HSK3", "HSK5"]:
        print(f"\n--- {level} 级别 ---")
        test_multilingual_ask(
            question=question,
            hsk_level=level,
            user_language="en"
        )
    
    print("\n" + "="*70)
    print("✅ 所有测试完成！")
    print("="*70)

if __name__ == '__main__':
    run_all_tests()
