# 多模态AI古诗教学平台 - 部署指南

## 项目概述

这是一个面向国际中文学习者的智能古诗学习平台，集成了AI问答、多媒体学习和个性化推荐功能。

## 技术栈

- **后端**: Flask + SQLite + JWT认证
- **前端**: HTML5 + TailwindCSS + JavaScript
- **AI服务**: 硅基流动 Qwen2.5-7B-Instruct API
- **数据库**: SQLite (Python内置)
- **数据可视化**: Chart.js

## 功能特性

### ✅ 已实现功能

1. **用户管理系统**
   - 用户注册/登录
   - JWT认证和会话管理
   - 密码加密存储（bcrypt）

2. **古诗数据库**
   - 10首经典唐诗数据
   - 包含原文、翻译、背景、注释
   - 难度分级和标签系统

3. **AI问答模块**
   - 字词解析
   - 背景介绍
   - 意境赏析
   - 自由问答
   - 集成硅基流动Qwen API

4. **练习系统**
   - 4种题型：字词释义、意象识别、情感判断、内容理解
   - AI自动生成练习题
   - 在线答题和成绩记录

5. **学习记录系统**
   - 自动追踪学习行为
   - 阅读时长统计
   - 字词查询记录
   - AI交互次数统计

6. **个人仪表板**
   - 学习进度展示
   - 数据可视化图表
   - 学习成就系统
   - 个性化推荐

7. **多媒体支持**
   - TTS语音朗读（浏览器内置）
   - 视频播放器框架（待扩展）

## 快速部署

### 1. 环境准备

```bash
# 确保已安装Python 3.8+
python --version

# 克隆项目（如果从git）
git clone <repository-url>
cd poem_project/code
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 环境配置

编辑 `.env` 文件，确保API密钥正确：

```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=jwt-secret-key-here
QWEN_API_KEY=sk-zzyesjjoxlxlfptbpwjnrxvxybunudvbqbaysrddqljqeiqf
QWEN_API_URL=https://api.siliconflow.cn/v1/chat/completions
DATABASE_URL=sqlite:///poem_platform.db
```

### 4. 初始化数据库

```bash
python init_db.py
```

### 5. 启动服务

```bash
python app.py
```

服务将在 `http://localhost:5000` 启动

### 6. 访问应用

- **API文档**: http://localhost:5000/api-docs
- **古诗选择**: http://localhost:5000/poems
- **学习仪表板**: http://localhost:5000/dashboard

## API接口文档

### 认证接口

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/profile` - 获取用户信息

### 古诗接口

- `GET /api/poems` - 获取古诗列表
- `GET /api/poems/{id}` - 获取古诗详情
- `POST /api/poems/{id}/start-learning` - 开始学习
- `GET /api/poems/recommend` - 获取推荐古诗

### AI问答接口

- `POST /api/ai/word-analysis` - 字词解析
- `POST /api/ai/background-explanation` - 背景介绍
- `POST /api/ai/artistic-analysis` - 意境赏析
- `POST /api/ai/general-question` - 一般问答

### 练习接口

- `GET /api/exercises/poem/{id}` - 获取练习题
- `POST /api/exercises/generate/{id}` - 生成练习题
- `POST /api/exercises/submit` - 提交答案

### 仪表板接口

- `GET /api/dashboard/overview` - 概览数据
- `GET /api/dashboard/learning-trends` - 学习趋势
- `GET /api/dashboard/achievements` - 学习成就

## 数据库结构

### 主要表结构

1. **users** - 用户表
2. **poems** - 古诗表
3. **learning_records** - 学习记录表
4. **exercises** - 练习题表
5. **user_exercise_records** - 用户练习记录表
6. **qa_records** - 问答记录表

## 项目结构

```
poem_project/
├── app.py                  # Flask应用主文件
├── init_db.py             # 数据库初始化脚本
├── requirements.txt       # Python依赖
├── .env                   # 环境变量配置
├── models/                # 数据模型
│   ├── __init__.py
│   ├── user.py
│   ├── poem.py
│   ├── learning_record.py
│   ├── exercise.py
│   └── qa_record.py
├── routes/                # API路由
│   ├── auth.py
│   ├── poems.py
│   ├── ai_chat.py
│   ├── exercises.py
│   ├── learning.py
│   └── dashboard.py
├── services/              # 业务逻辑服务
│   └── qwen_service.py
├── templates/             # HTML模板
│   ├── index.html         # API文档
│   ├── poems_list.html    # 古诗选择
│   ├── poem_study.html    # 古诗学习
│   └── dashboard.html     # 学习仪表板
├── static/                # 静态文件
│   ├── videos/
│   ├── audio/
│   ├── css/
│   └── js/
└── docs/                  # 文档
    └── deployment.md
```

## 扩展建议

### 短期优化

1. **多媒体内容**
   - 添加真实的古诗意境视频
   - 集成专业TTS服务
   - 支持背景音乐播放

2. **用户体验**
   - 响应式设计优化
   - 加载状态优化
   - 错误处理完善

3. **数据分析**
   - 更详细的学习分析
   - 学习路径推荐
   - 难点识别系统

### 长期扩展

1. **内容扩展**
   - 增加更多古诗词
   - 支持宋词、元曲
   - 添加现代诗歌

2. **功能增强**
   - 社交学习功能
   - 学习小组系统
   - 竞赛和排行榜

3. **技术升级**
   - 微服务架构
   - 容器化部署
   - 分布式数据库

## 注意事项

1. **API密钥安全**
   - 不要将API密钥提交到版本控制
   - 生产环境使用环境变量

2. **数据备份**
   - 定期备份SQLite数据库
   - 考虑使用更robust的数据库

3. **性能优化**
   - 添加缓存机制
   - 优化数据库查询
   - 考虑CDN加速

## 联系方式

如有问题或建议，请联系开发团队。

---

**项目状态**: 开发完成，可用于演示和测试
**最后更新**: 2025年11月12日
