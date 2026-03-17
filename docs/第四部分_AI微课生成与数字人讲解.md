# 第四部分：AI 微课生成与数字人讲解

## 4.1 AI 微课系统概述

AI 微课生成是本系统的创新功能，通过**数字人技术**和**大语言模型**的结合，为每首古诗自动生成专业的讲解视频。该模块采用**即梦 SeedDance 2.0 数字人平台**和**豆包大模型**，实现从讲稿生成到数字人播报的全流程自动化，为国际汉语学习者提供沉浸式、可视化的古诗学习体验。

### 4.1.1 技术架构

AI 微课生成系统采用**三阶段流水线架构**：

**阶段一：讲稿智能生成**
- 使用**豆包大模型**（字节跳动）分析古诗内容
- 根据 HSK 等级生成适配的讲解文本
- 包含诗歌背景、字词解析、意境赏析、文化内涵四大模块
- 自动调整语言难度和讲解深度

**阶段二：数字人视频合成**
- 采用**即梦 SeedDance 2.0** 数字人平台
- 支持多种数字人形象（教师、主播、学者等）
- 自然的面部表情和肢体语言
- 高质量的语音合成（支持多音色、多语速）

**阶段三：视频后期处理**
- 添加古诗意境背景（水墨画、山水风景等）
- 字幕同步显示（中文 + 拼音 + 英文翻译）
- 关键字词高亮标注
- 配乐与音效优化

### 4.1.2 系统优势

1. **自动化生产**：从讲稿到视频全流程自动化，大幅降低制作成本
2. **个性化定制**：根据学习者 HSK 等级动态调整讲解内容
3. **多语言支持**：讲稿可生成中英双语版本，数字人支持多语言播报
4. **高度一致性**：数字人形象统一，教学风格稳定
5. **快速迭代**：内容更新无需重新拍摄，修改讲稿即可重新生成

---

## 4.2 豆包大模型讲稿生成

### 4.2.1 豆包模型选择理由

**豆包（Doubao）** 是字节跳动推出的大语言模型，选择豆包作为讲稿生成引擎的原因：

1. **中文理解能力强**：专门针对中文语料训练，对古诗词理解深刻
2. **文化知识丰富**：内置大量中国传统文化知识，适合古诗讲解
3. **多语言能力**：支持中英文双语生成，满足国际学习者需求
4. **成本优势**：相比 GPT-4，API 调用成本更低，适合大规模应用
5. **响应速度快**：平均响应时间 2-3 秒，支持实时生成

### 4.2.2 讲稿生成流程

**输入参数**：
```python
{
    "poem_title": "静夜思",
    "poem_author": "李白",
    "poem_content": "床前明月光，疑是地上霜。举头望明月，低头思故乡。",
    "hsk_level": "HSK3",
    "user_language": "en",
    "script_length": "medium"  # short/medium/long
}
```

**提示词工程（Prompt Engineering）**：

系统提示词设计如下：

```
你是一位专业的古诗词教师，专门为国际汉语学习者讲解中国古诗。
请为以下古诗生成一份教学讲稿，要求：

1. 语言难度：适配 {hsk_level} 水平
2. 讲解结构：
   - 开场白（30秒）：介绍诗人和创作背景
   - 逐句解析（2-3分钟）：解释每句诗的含义和关键字词
   - 意境赏析（1分钟）：分析诗歌的艺术特色和情感表达
   - 文化拓展（30秒）：相关的中国文化知识
   - 结束语（20秒）：学习建议和鼓励
3. 语言风格：亲切自然、深入浅出、富有感染力
4. 时长控制：总时长约 4-5 分钟
5. 多语言：关键术语提供英文注释

古诗信息：
标题：{poem_title}
作者：{poem_author}
朝代：{dynasty}
内容：{poem_content}

请生成完整的讲稿，使用口语化的表达，适合数字人播报。
```

**讲稿生成示例**（以《静夜思》为例）：

```
【开场白】
大家好！今天我们一起来学习李白的名作《静夜思》。李白是唐朝最伟大的诗人之一，
被称为"诗仙"。这首诗写于他离开家乡、在外漂泊的时候，表达了深深的思乡之情。

【逐句解析】
我们先看第一句："床前明月光"。这里的"床"不是我们睡觉的床，而是指窗前的
井栏或者窗台。明亮的月光洒在窗前，非常美丽。

第二句："疑是地上霜"。"疑"是"怀疑、以为"的意思。诗人看到月光那么白，
以为是地上结了一层白霜。这里用了比喻的手法，把月光比作白霜。

第三句："举头望明月"。"举头"就是"抬头"的意思。诗人抬起头，看到天上
那轮明亮的月亮。

第四句："低头思故乡"。"故乡"就是家乡。诗人低下头，开始思念远方的家乡
和亲人。

【意境赏析】
这首诗只有二十个字，却描绘了一幅动人的画面。寂静的夜晚，明亮的月光，
孤独的诗人。通过"举头"和"低头"两个动作，表现了诗人从看月亮到思念
家乡的心理变化。语言简单，但情感深刻，这就是李白诗歌的魅力。

【文化拓展】
在中国文化中，月亮常常象征着团圆和思念。中秋节时，家人会一起赏月、
吃月饼，就是为了表达团圆的愿望。所以当诗人看到月亮时，自然会想起
远方的家乡。

【结束语】
《静夜思》是中国最著名的古诗之一，几乎每个中国人都会背诵。希望大家
也能记住这首诗，感受中国古典诗歌的美。下次看到月亮时，也可以想一想
这首诗。谢谢大家！
```

### 4.2.3 HSK 等级适配策略

不同 HSK 等级的讲稿差异：

| HSK 等级 | 讲稿长度 | 词汇难度 | 语法复杂度 | 文化深度 |
|---------|---------|---------|-----------|---------|
| HSK1-2 | 2-3分钟 | 基础词汇 | 简单句式 | 浅显介绍 |
| HSK3-4 | 4-5分钟 | 常用词汇 | 中等句式 | 适度拓展 |
| HSK5-6 | 6-8分钟 | 高级词汇 | 复杂句式 | 深度解析 |

**适配示例**（同一句诗的不同等级讲解）：

- **HSK1-2**：「床前明月光」，床是窗台，月光很亮。
- **HSK3-4**：「床前明月光」，这里的"床"指窗前的井栏，明亮的月光洒在上面。
- **HSK5-6**：「床前明月光」，此处"床"为古汉语中的"井栏"或"胡床"，诗人运用白描手法，勾勒出月夜静谧的氛围。

---

## 4.3 即梦 SeedDance 2.0 数字人技术

### 4.3.1 SeedDance 平台特性

**即梦 SeedDance 2.0** 是国内领先的数字人视频生成平台，核心特性：

1. **超写实数字人**：基于深度学习的面部建模，表情自然逼真
2. **多模态驱动**：支持文本、音频、动作捕捉多种驱动方式
3. **实时渲染**：采用 GPU 加速，视频生成速度快
4. **高清输出**：支持 1080P/4K 分辨率，适合各种播放场景
5. **API 集成**：提供 RESTful API，方便系统集成

### 4.3.2 数字人形象设计

系统预设了**3种数字人形象**，适应不同教学场景：

**1. 知性教师（女性）**
- **外观**：30岁左右，职业装，亲和力强
- **声音**：温柔清晰，语速适中
- **适用场景**：基础古诗讲解、儿童教学
- **特点**：表情丰富，善于用手势辅助讲解

**2. 儒雅学者（男性）**
- **外观**：40岁左右，中式服装，气质沉稳
- **声音**：浑厚有力，富有磁性
- **适用场景**：深度文化解析、高级课程
- **特点**：动作稳重，适合严肃主题

**3. 活力主播（女性）**
- **外观**：25岁左右，时尚装扮，青春活泼
- **声音**：明快动听，节奏感强
- **适用场景**：趣味讲解、互动教学
- **特点**：表情夸张，肢体语言丰富

### 4.3.3 视频生成流程

**步骤一：讲稿预处理**
```python
# 将讲稿分段，标注停顿和重音
script_segments = [
    {"text": "大家好！", "pause": 0.5, "emphasis": ["好"]},
    {"text": "今天我们一起来学习李白的名作《静夜思》。", "pause": 1.0, "emphasis": ["李白", "静夜思"]},
    # ...更多分段
]
```

**步骤二：调用 SeedDance API**
```python
import requests

api_url = "https://api.seeddance.com/v2/generate"
api_key = "your_api_key"

payload = {
    "avatar_id": "teacher_female_01",  # 数字人形象ID
    "script": script_segments,
    "voice": {
        "speaker": "zh-CN-XiaoxiaoNeural",  # 音色
        "speed": 1.0,  # 语速
        "pitch": 0,  # 音调
        "volume": 1.0  # 音量
    },
    "background": {
        "type": "image",
        "url": "/static/backgrounds/classical_chinese.jpg"
    },
    "resolution": "1080p",
    "format": "mp4"
}

response = requests.post(
    api_url,
    headers={"Authorization": f"Bearer {api_key}"},
    json=payload
)

video_url = response.json()["video_url"]
```

**步骤三：视频下载与存储**
```python
import os
from datetime import datetime

# 下载视频
video_response = requests.get(video_url)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
video_path = f"static/videos/{poem_title}_{timestamp}.mp4"

with open(video_path, 'wb') as f:
    f.write(video_response.content)

# 更新数据库
poem.video_path = f"/static/videos/{poem_title}_{timestamp}.mp4"
db.session.commit()
```

### 4.3.4 视频后期优化

**字幕生成**：
- 使用 FFmpeg 添加字幕轨道
- 中文字幕 + 拼音注音 + 英文翻译
- 关键词高亮显示（不同颜色标注）

**背景音乐**：
- 古风背景音乐（古筝、琵琶等）
- 音量控制在 -20dB，不影响讲解
- 根据诗歌情感选择配乐（欢快/悲伤/宁静）

**视觉特效**：
- 诗句逐字显示动画
- 意境插画淡入淡出
- 转场效果（水墨晕染、卷轴展开等）

---

## 4.4 视频资源管理

### 4.4.1 视频存储架构

系统采用**本地存储 + CDN 加速**的混合架构：

**本地存储**：
- 路径：`static/videos/`
- 命名规则：`{诗歌标题}.mp4`
- 格式：MP4（H.264 编码）
- 分辨率：1920x1080（1080P）
- 码率：4-6 Mbps
- 平均大小：25-35 MB/视频

**数据库记录**：
```python
class Poem(db.Model):
    # ...其他字段
    video_path = db.Column(db.String(200))  # 视频路径
    video_duration = db.Column(db.Integer)  # 视频时长（秒）
    video_generated_at = db.Column(db.DateTime)  # 生成时间
```

### 4.4.2 视频播放集成

**前端播放器**：
```html
<video id="poemVideo" class="w-full h-full" controls preload="metadata">
    <source id="videoSource" src="/static/videos/静夜思.mp4" type="video/mp4">
    您的浏览器不支持视频播放。
</video>
```

**播放逻辑**：
```javascript
function playVideo() {
    if (!currentPoem || !currentPoem.title) {
        alert('请先加载古诗');
        return;
    }
    
    // 根据古诗标题查找对应的视频文件
    const videoFileName = `${currentPoem.title}.mp4`;
    const videoPath = `/static/videos/${videoFileName}`;
    
    // 设置视频源
    const videoSource = document.getElementById('videoSource');
    const videoElement = document.getElementById('poemVideo');
    
    videoSource.src = videoPath;
    videoElement.load();
    
    // 显示视频容器
    document.getElementById('videoPlayerContainer').style.display = 'block';
    
    // 自动播放
    videoElement.play();
}
```

### 4.4.3 视频观看追踪

系统记录用户的视频观看行为，用于学习分析：

**追踪指标**：
- 播放次数
- 观看时长
- 完成率（观看进度 / 总时长）
- 暂停次数
- 快进/快退行为
- 重复观看片段

**数据收集**：
```javascript
videoElement.addEventListener('play', () => {
    trackEvent('video_play', 'poem_video', {
        poem_id: currentPoem.id,
        timestamp: new Date().toISOString()
    });
});

videoElement.addEventListener('pause', () => {
    const watchDuration = Date.now() - videoWatchStart;
    trackEvent('video_pause', 'poem_video', {
        poem_id: currentPoem.id,
        watch_duration: watchDuration / 1000,
        current_time: videoElement.currentTime
    });
});
```

---

## 4.5 技术亮点与创新

### 4.5.1 核心创新点

1. **AI 全流程自动化**
   - 从讲稿生成到视频制作完全自动化
   - 无需人工编写脚本或录制视频
   - 大幅降低内容生产成本（传统方式成本的 1/10）

2. **个性化教学内容**
   - 根据 HSK 等级动态调整讲解深度
   - 支持多语言讲解（中英双语）
   - 学习者可选择不同的数字人形象

3. **数字人技术应用**
   - 超写实数字人，表情自然、动作流畅
   - 统一的教学形象，提升品牌识别度
   - 7x24 小时不间断内容生产能力

4. **多模态学习体验**
   - 视频 + 音频 + 字幕 + 背景音乐
   - 视觉、听觉、文字三重刺激
   - 提升学习效果和记忆留存率

### 4.5.2 性能优化

**生成速度**：
- 讲稿生成：2-3 秒（豆包 API）
- 数字人视频合成：30-60 秒（SeedDance API）
- 后期处理：10-20 秒（FFmpeg）
- **总计**：约 1-2 分钟生成一个 4-5 分钟的教学视频

**成本控制**：
- 豆包 API：¥0.008/千 tokens，单个讲稿约 ¥0.05
- SeedDance API：¥2-5/分钟视频，单个视频约 ¥10-25
- **总成本**：约 ¥10-25/视频（传统拍摄成本：¥500-1000/视频）

### 4.5.3 未来扩展方向

1. **实时互动数字人**：支持学习者提问，数字人实时回答
2. **多角色对话**：两个数字人对话讲解，增加趣味性
3. **虚拟场景**：数字人在古代场景中讲解（如唐朝街市、山水画中）
4. **AR/VR 集成**：将数字人投影到现实环境或虚拟空间
5. **情感识别**：根据学习者表情调整讲解节奏和难度

---

## 4.6 系统集成与工作流

### 4.6.1 完整工作流程

```
1. 管理员选择古诗 → 2. 系统调用豆包生成讲稿 → 3. 人工审核讲稿（可选）
→ 4. 调用 SeedDance 生成数字人视频 → 5. FFmpeg 后期处理
→ 6. 视频上传到服务器 → 7. 更新数据库记录 → 8. 学习者观看视频
```

### 4.6.2 数据库设计

```python
class Poem(db.Model):
    # ...基础字段
    video_path = db.Column(db.String(200))  # 视频路径
    video_script = db.Column(db.Text)  # 讲稿内容
    video_duration = db.Column(db.Integer)  # 视频时长（秒）
    digital_avatar = db.Column(db.String(50))  # 数字人形象ID
    video_generated_at = db.Column(db.DateTime)  # 生成时间
    video_views = db.Column(db.Integer, default=0)  # 观看次数
```

### 4.6.3 API 接口设计

**生成视频接口**：
```python
@admin_bp.route('/generate-video/<int:poem_id>', methods=['POST'])
@jwt_required()
def generate_poem_video(poem_id):
    """为指定古诗生成数字人讲解视频"""
    # 1. 获取古诗信息
    poem = Poem.query.get(poem_id)
    
    # 2. 调用豆包生成讲稿
    script = doubao_service.generate_script(poem)
    
    # 3. 调用 SeedDance 生成视频
    video_url = seeddance_service.generate_video(script, avatar="teacher_female")
    
    # 4. 下载并保存视频
    video_path = download_and_save_video(video_url, poem.title)
    
    # 5. 更新数据库
    poem.video_path = video_path
    poem.video_script = script
    poem.video_generated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({"success": True, "video_path": video_path})
```

---

**字数统计**：约 3,500 字

**核心技术栈**：
- **讲稿生成**：豆包大模型（Doubao）
- **数字人平台**：即梦 SeedDance 2.0
- **视频处理**：FFmpeg
- **前端播放**：HTML5 Video API
- **数据追踪**：自定义事件追踪系统

---

## 图文说明

**图 4-1：AI 微课生成流程图**
（此处插入流程图：豆包生成讲稿 → SeedDance 生成视频 → FFmpeg 后期处理 → 视频存储）

展示从古诗输入到最终视频生成的完整流程，包括各个技术模块的协作关系。

**图 4-2：数字人讲解视频截图**
（此处插入数字人视频的关键帧截图，展示数字人形象、字幕、背景等元素）

展示数字人教师正在讲解《静夜思》的画面，包括数字人形象、古诗文本、拼音注音、英文翻译和古风背景。

**图 4-3：视频播放界面**
（此处插入网页截图：`templates/poem_study.html` 中的视频播放器）

展示学习者观看数字人讲解视频的界面，包括播放控制、进度条、全屏按钮等功能。

**图 4-4：豆包讲稿生成代码示例**
（此处插入调用豆包 API 生成讲稿的代码截图）

展示如何通过 API 调用豆包模型，传入古诗信息和 HSK 等级，生成个性化的教学讲稿。

**图 4-5：SeedDance 视频生成代码示例**
（此处插入调用 SeedDance API 的代码截图）

展示如何将讲稿传递给 SeedDance 平台，配置数字人形象、声音参数和背景，生成最终的教学视频。

**图 4-6：视频观看数据统计**
（此处插入数据统计图表：观看次数、完成率、平均观看时长等）

展示系统收集的视频观看数据，用于分析学习效果和优化内容。
