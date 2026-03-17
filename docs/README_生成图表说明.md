# 系统架构图和ER图生成说明

## 📦 安装依赖

```bash
pip install graphviz
```

**重要**: 还需要安装 Graphviz 软件本身
- Windows: https://graphviz.org/download/ 下载安装包
- 安装后将 `bin` 目录添加到系统环境变量 PATH 中
- 例如: `C:\Program Files\Graphviz\bin`

## 🎨 生成系统架构图

```bash
cd e:\poem_project\code\docs
python generate_architecture_diagram.py
```

生成文件: `system_architecture.png`

**架构图包含**:
- 前端层（HTML/CSS/JS + 页面模块 + 追踪系统）
- 后端层（Flask + JWT认证 + API路由）
- 服务层（Qwen AI服务 + 语音服务）
- 数据层（SQLAlchemy ORM + SQLite数据库）
- 外部服务（SiliconFlow API + Edge TTS）

## 📊 生成数据库ER图

```bash
cd e:\poem_project\code\docs
python generate_er_diagram.py
```

生成文件: `database_er_diagram.png`

**ER图包含**:
- 8个核心数据表及其字段
- 表之间的外键关系
- 主键标记（🔑）
- 字段类型信息

## 📋 数据库表说明

| 表名 | 说明 | 核心字段 |
|------|------|----------|
| users | 用户信息 | username, email, hsk_level, native_language |
| poems | 古诗数据 | title, author, content, video_path, audio_path |
| learning_records | 学习记录 | reading_time, video_watch_time, completion_rate |
| exercises | 练习题库 | question_type, question, correct_answer |
| user_exercise_records | 答题记录 | user_answer, is_correct, score |
| qa_records | AI问答记录 | question, answer, question_type, user_rating |
| attention_tracking | 注意力追踪 | mouse_movements, focus_duration, engagement_score |
| learning_session | 学习会话 | start_time, duration_seconds, interaction_data |
| interaction_event | 交互事件 | event_type, event_target, event_data |

## 🔗 表关系说明

- `users` ← `learning_records` (一对多)
- `users` ← `user_exercise_records` (一对多)
- `users` ← `qa_records` (一对多)
- `users` ← `learning_session` (一对多)
- `poems` ← `learning_records` (一对多)
- `poems` ← `exercises` (一对多)
- `poems` ← `qa_records` (一对多)
- `exercises` ← `user_exercise_records` (一对多)
- `learning_session` ← `interaction_event` (一对多)

## 💡 使用建议

1. **论文写作**: 将生成的PNG图片插入到论文的"系统架构与总体设计"部分
2. **图片说明**: 为每张图添加图注（Figure 1: 系统架构图 / Figure 2: 数据库ER图）
3. **文字配合**: 在图片前后添加文字说明，解释技术选型理由
4. **高清输出**: 如需更高分辨率，可修改代码中的 `format='png'` 为 `format='svg'`
