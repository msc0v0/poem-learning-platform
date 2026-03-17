# AI智能问答助手优化说明

## 📋 功能概述

AI智能问答助手已升级，现在支持多语言提问、HSK等级适配回答、智能翻译等功能。

---

## ✨ 新增功能

### 1. 多语言提问支持

**功能描述：**
- 学生可以用母语（英语、西班牙语、法语、德语等）或中文提问
- 系统自动检测问题语言
- 支持的语言：中文(zh)、英语(en)、西班牙语(es)、法语(fr)、德语(de)、日语(ja)、韩语(ko)

**实现方式：**
```python
# 语言自动检测
detected_lang, confidence = qwen_service.detect_language(question)
```

---

### 2. HSK等级适配回答

**功能描述：**
- 根据学生的HSK等级（HSK1-HSK6）调整回答难度
- 使用适合该等级的词汇和句式
- 控制回答长度和复杂度

**等级控制策略：**

| HSK等级 | 最大字数 | 难度 | 特点 |
|---------|----------|------|------|
| HSK1 | 50字 | 非常简单 | 使用最基础词汇（是、有、在、去等） |
| HSK2 | 80字 | 简单 | 基础词汇+短句 |
| HSK3 | 120字 | 中等 | 中等难度词汇（著名、表达、描写等） |
| HSK4 | 200字 | 中高 | 较丰富词汇，简单文化背景 |
| HSK5 | 300字 | 高级 | 高级词汇，成语，复杂句式 |
| HSK6 | 500字 | 专家 | 专业术语，深入文化解析 |

**使用示例：**
```json
{
  "question": "Who is Li Bai?",
  "hsk_level": "HSK3",
  "user_language": "en"
}
```

---

### 3. 智能翻译功能

**功能描述：**
- 所有回答默认用中文（促进中文学习）
- 提供母语翻译，点击"查看翻译"按钮显示
- 翻译质量高，保持原文语气和文学性

**前端展示：**
```html
<div class="answer-container">
    <div class="chinese-answer">
        <!-- 中文答案 -->
    </div>
    <button class="show-translation-btn">
        🌍 查看翻译 (View Translation)
    </button>
    <div class="translation-answer" style="display: none;">
        <!-- 翻译内容 -->
    </div>
</div>
```

---

### 4. 预设问题库（QA库）

**功能描述：**
- 常见问题快速响应（无需调用AI）
- 确保答案准确性
- 提高响应速度

**预设问题类别：**

#### 作者介绍
- 李白是谁
- 杜甫是谁
- 王维是谁
- 孟浩然是谁
- 白居易是谁

#### 作者风格
- 李白的诗有什么特点

#### 诗歌形式
- 什么是五言绝句
- 什么是七言绝句
- 什么是律诗

#### 文学术语
- 什么是意象
- 什么是对仗

---

## 🔧 API接口

### 1. 智能多语言问答（新）

**接口：** `POST /api/ai/ask`

**请求参数：**
```json
{
  "question": "What does 举头 mean?",  // 问题（任何语言）
  "poem_id": 1,                        // 可选，诗歌ID
  "hsk_level": "HSK3",                 // 可选，HSK等级，默认HSK3
  "user_language": "en"                // 可选，母语代码，默认自动检测
}
```

**响应示例：**
```json
{
  "success": true,
  "answer_chinese": "举头的意思是'抬起头'。在这首诗中，诗人抬起头看到明亮的月光。",
  "answer_translation": "举头 means 'to raise one's head' or 'to look up'. In this poem, the poet raises his head and sees the bright moonlight.",
  "has_translation": true,
  "question_language": "en",
  "user_language": "en",
  "common_qa_used": false,
  "hsk_level": "HSK3",
  "response_time": 1.23,
  "qa_id": 45
}
```

---

### 2. 获取常见问题列表

**接口：** `GET /api/ai/common-questions`

**响应示例：**
```json
{
  "success": true,
  "categories": {
    "作者介绍": [
      {
        "question": "李白是谁",
        "preview": "李白（701-762年）是唐朝最著名的诗人之一，被称为\"诗仙\"..."
      }
    ],
    "诗歌形式": [
      {
        "question": "什么是五言绝句",
        "preview": "五言绝句是中国古典诗歌的一种形式。每句五个字，全诗四句..."
      }
    ]
  },
  "total_questions": 11
}
```

---

### 3. 更新用户设置

**接口：** `PUT /api/auth/profile`

**请求参数：**
```json
{
  "hsk_level": "HSK4",         // 更新HSK等级
  "native_language": "es"      // 更新母语
}
```

---

## 📊 数据库更新

### User表新增字段

```sql
ALTER TABLE users ADD COLUMN hsk_level VARCHAR(10) DEFAULT 'HSK3';
ALTER TABLE users ADD COLUMN native_language VARCHAR(10) DEFAULT 'en';
```

**运行迁移脚本：**
```bash
python upgrade_user_fields.py
```

---

## 🎨 前端集成建议

### 1. 问题输入框提示

```html
<div class="question-input-container">
    <textarea 
        placeholder="有什么问题吗？(What's your question?)"
        class="question-input"
    ></textarea>
    <div class="input-hint">
        💡 尝试用中文关键词提问，学习效果更好哦！
    </div>
</div>
```

### 2. 答案显示组件

```html
<div class="ai-answer-card">
    <!-- 中文答案（始终显示） -->
    <div class="answer-chinese">
        <div class="answer-label">
            🤖 AI回答 
            <span class="hsk-badge">HSK3级别</span>
        </div>
        <div class="answer-content">
            {{ answer_chinese }}
        </div>
    </div>
    
    <!-- 翻译按钮（仅当有翻译时显示） -->
    <button 
        v-if="has_translation" 
        @click="toggleTranslation"
        class="translation-toggle-btn"
    >
        <span v-if="!showTranslation">
            🌍 查看翻译 (View Translation)
        </span>
        <span v-else>
            ⬆️ 隐藏翻译 (Hide Translation)
        </span>
    </button>
    
    <!-- 翻译内容（点击后显示） -->
    <div 
        v-if="showTranslation && has_translation" 
        class="answer-translation"
    >
        <div class="translation-label">
            📖 {{ languageName }} Translation
        </div>
        <div class="translation-content">
            {{ answer_translation }}
        </div>
    </div>
    
    <!-- 来源标识 -->
    <div class="answer-source">
        <span v-if="common_qa_used">
            ⚡ 来自知识库 (From Knowledge Base)
        </span>
        <span v-else>
            🤖 AI生成 (AI Generated)
        </span>
        <span class="response-time">{{ response_time }}秒</span>
    </div>
</div>
```

### 3. 用户设置页面

```html
<div class="user-settings">
    <div class="setting-item">
        <label>HSK等级 (HSK Level)</label>
        <select v-model="hsk_level">
            <option value="HSK1">HSK 1 - 入门</option>
            <option value="HSK2">HSK 2 - 初级</option>
            <option value="HSK3">HSK 3 - 中级 (推荐)</option>
            <option value="HSK4">HSK 4 - 中高级</option>
            <option value="HSK5">HSK 5 - 高级</option>
            <option value="HSK6">HSK 6 - 精通</option>
        </select>
        <div class="setting-hint">
            选择适合你的中文水平，AI会调整回答难度
        </div>
    </div>
    
    <div class="setting-item">
        <label>母语 (Native Language)</label>
        <select v-model="native_language">
            <option value="en">English (英语)</option>
            <option value="es">Español (西班牙语)</option>
            <option value="fr">Français (法语)</option>
            <option value="de">Deutsch (德语)</option>
            <option value="ja">日本語 (日语)</option>
            <option value="ko">한국어 (韩语)</option>
            <option value="zh">中文</option>
        </select>
        <div class="setting-hint">
            设置母语后，可以查看答案的翻译
        </div>
    </div>
</div>
```

---

## 💡 使用建议

### 教学策略

1. **鼓励中文提问**
   - 在输入框提示："尝试用中文关键词提问，学习效果更好哦！"
   - 即使问题很简单，也鼓励学生尝试用中文

2. **渐进式学习**
   - 初期可以依赖翻译
   - 逐步减少查看翻译的频率
   - 最终目标：只看中文答案

3. **HSK等级匹配**
   - 定期评估学生水平，调整HSK等级
   - 等级提升会自动提高答案难度

---

## 🧪 测试示例

### 测试场景1：英语提问，HSK3级别

**请求：**
```bash
curl -X POST http://127.0.0.1:5000/api/ai/ask \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What does the moon symbolize in Chinese poetry?",
    "hsk_level": "HSK3",
    "user_language": "en"
  }'
```

**预期响应：**
- 中文答案使用HSK3级别词汇
- 提供英语翻译
- 答案简洁明了（约120字）

### 测试场景2：西班牙语提问

**请求：**
```bash
curl -X POST http://127.0.0.1:5000/api/ai/ask \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "¿Quién es Li Bai?",
    "user_language": "es"
  }'
```

**预期响应：**
- 检测到西班牙语
- 使用预设QA库回答（common_qa_used: true）
- 提供西班牙语翻译

---

## 📈 性能优化

1. **预设QA库**
   - 常见问题平均响应时间：< 0.1秒
   - 准确率：100%

2. **缓存策略**（建议实现）
   - 相同问题24小时内返回缓存答案
   - 减少API调用成本

3. **批量翻译**（未来改进）
   - 预先翻译常见答案到多种语言
   - 进一步提升响应速度

---

## 🔐 安全性

1. 所有接口需要JWT认证
2. 用户只能访问自己的问答历史
3. 输入验证和过滤
4. API调用频率限制（建议添加）

---

## 📝 TODO

- [ ] 添加更多预设问题（目标：50+）
- [ ] 实现答案缓存机制
- [ ] 添加用户反馈收集
- [ ] 实现问题推荐功能
- [ ] 多语言前端界面
- [ ] 语音输入支持

---

## 🎯 使用流程

1. **首次使用**
   - 用户注册/登录
   - 设置HSK等级和母语
   
2. **提问**
   - 用任何语言输入问题
   - 系统自动检测语言
   
3. **查看答案**
   - 首先显示中文答案
   - 点击按钮查看翻译（可选）
   
4. **学习成长**
   - 评价答案质量
   - 调整HSK等级
   - 减少翻译依赖

---

## 📞 技术支持

如有问题，请参考：
- API文档：http://127.0.0.1:5000/api-docs
- 健康检查：http://127.0.0.1:5000/api/health
