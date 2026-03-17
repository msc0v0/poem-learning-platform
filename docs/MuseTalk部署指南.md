# MuseTalk 数字人部署指南

## 项目简介

MuseTalk 是腾讯音乐开源的实时高质量口型同步数字人生成系统，非常适合古诗讲解等教育场景。

- **项目地址**: https://github.com/TMElyralab/MuseTalk
- **技术特点**: 潜在空间单步生成，非扩散模型，速度快质量高
- **推荐显卡**: RTX 4090（推理显存约 6-8GB）

## 一、环境准备

### 1.1 系统要求

```
操作系统: Windows/Linux
Python: 3.10
CUDA: 11.7 或更高
显存: 8GB+ (RTX 4090 完美适配)
硬盘: 20GB+ (模型权重约 10GB)
```

### 1.2 创建虚拟环境

```bash
# 创建 conda 环境
conda create -n musetalk python=3.10
conda activate musetalk

# 或使用 venv
python -m venv musetalk_env
# Windows
musetalk_env\Scripts\activate
# Linux
source musetalk_env/bin/activate
```

## 二、安装步骤

### 2.1 克隆项目

```bash
git clone https://github.com/TMElyralab/MuseTalk.git
cd MuseTalk
```

### 2.2 安装 PyTorch

**CUDA 11.7 版本**:
```bash
pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu117
```

**CUDA 11.8 版本**:
```bash
pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu118
```

**验证安装**:
```python
python -c "import torch; print(torch.cuda.is_available()); print(torch.version.cuda)"
```

### 2.3 安装依赖包

```bash
# 安装基础依赖
pip install -r requirements.txt

# 安装 MMlab 系列包（用于人脸检测）
pip install --no-cache-dir -U openmim
mim install mmengine
mim install "mmcv>=2.0.1"
mim install "mmdet>=3.1.0"
mim install "mmpose>=1.1.0"
```

### 2.4 安装 FFmpeg

**Windows**:
1. 下载 FFmpeg: https://www.gyan.dev/ffmpeg/builds/
2. 解压到 `C:\ffmpeg`
3. 添加环境变量: `C:\ffmpeg\bin`
4. 验证: `ffmpeg -version`

**Linux**:
```bash
sudo apt update
sudo apt install ffmpeg
```

### 2.5 下载模型权重

创建模型目录并下载权重:

```bash
mkdir -p models
cd models

# 下载权重（约 10GB）
# 方式1: 使用 git lfs
git lfs install
git clone https://huggingface.co/TMElyralab/MuseTalk

# 方式2: 手动下载
# 访问 https://huggingface.co/TMElyralab/MuseTalk/tree/main
# 下载以下文件到 models/musetalk 目录:
# - musetalk.json
# - pytorch_model.bin
# - whisper/tiny.pt
# - dwpose/dw-ll_ucoco_384.pth
# - face-parse-bisent/79999_iter.pth
# - sd-vae-ft-mse/...
```

**百度网盘备用** (如果 HuggingFace 下载慢):
- 链接: https://pan.baidu.com/s/1eF13O-8wyw4B3MtesctQyg
- 提取码: linl

## 三、使用方法

### 3.1 准备素材

**人物图片要求**:
- 格式: JPG/PNG
- 分辨率: 512x512 或更高
- 要求: 正面清晰人脸，最好包含肩膀
- 建议: 使用中景照片，背景简洁
- 推荐: 古风教师形象（适合古诗讲解）

**音频要求**:
- 格式: WAV/MP3
- 采样率: 16000Hz (自动转换)
- 时长: 建议 10 秒到 5 分钟
- 内容: 古诗讲解音频

### 3.2 目录结构

```
MuseTalk/
├── models/              # 模型权重
│   └── musetalk/
├── data/
│   ├── video/          # 参考视频（可选）
│   ├── image/          # 输入图片
│   └── audio/          # 输入音频
├── results/            # 输出结果
└── configs/            # 配置文件
```

### 3.3 推理生成

**基础命令**:
```bash
python inference.py \
  --avatar_id "teacher" \
  --video_path "data/video/teacher.mp4" \  # 可选：参考视频
  --audio_path "data/audio/poem_01.wav" \
  --bbox_shift 0
```

**从图片生成**:
```bash
python scripts/inference_single_image.py \
  --image_path "data/image/teacher.png" \
  --audio_path "data/audio/咏鹅_讲解.wav" \
  --result_dir "results/" \
  --fps 25
```

**批量处理**:
```bash
python scripts/batch_inference.py \
  --image_path "data/image/teacher.png" \
  --audio_dir "data/audio/" \
  --result_dir "results/"
```

### 3.4 Gradio Web UI (推荐)

启动可视化界面:
```bash
python app.py
```

访问: `http://localhost:7860`

界面操作:
1. 上传教师照片
2. 上传古诗讲解音频
3. 调整参数（可选）
4. 点击生成
5. 下载结果视频

## 四、参数调优

### 4.1 核心参数

```python
# configs/inference_config.yaml

inference:
  fps: 25                    # 帧率（推荐 25）
  batch_size: 8              # 批处理大小（4090 可用 8-16）
  output_vid_name: "result"  # 输出文件名
  
model:
  bbox_shift: 0              # 人脸框偏移（-5 到 5）
  use_float16: true          # 使用 FP16 加速（推荐）
  
quality:
  resolution: 512            # 输出分辨率
  enhance_face: true         # 人脸增强（可选）
```

### 4.2 性能优化

**4090 推荐配置**:
```yaml
batch_size: 16               # 充分利用显存
use_float16: true            # FP16 加速
enable_xformers: true        # 注意力机制优化
```

**显存不足时**:
```yaml
batch_size: 4
resolution: 256
use_float16: true
```

### 4.3 质量优化

```yaml
# 高质量输出
resolution: 512              # 或 768
fps: 30                      # 更流畅
enhance_face: true           # GFPGAN 人脸增强
super_resolution: true       # Real-ESRGAN 超分辨率（可选）
```

## 五、常见问题

### 5.1 安装问题

**问题**: `CUDA out of memory`
```bash
# 解决：减小 batch_size
batch_size: 4  # 改为 4 或 2
```

**问题**: `ffmpeg not found`
```bash
# Windows: 检查环境变量
echo %PATH%
# Linux: 重新安装
sudo apt install ffmpeg
```

**问题**: `MMPose 安装失败`
```bash
# 使用 conda 安装
conda install -c conda-forge mmcv
```

### 5.2 生成问题

**问题**: 口型不准确
```yaml
# 调整音频预处理
audio:
  denoise: true              # 降噪
  normalize: true            # 归一化
```

**问题**: 人脸抖动
```yaml
# 增加平滑
bbox_shift: 0                # 调整 -5 到 5
use_pose_smooth: true        # 启用姿态平滑
```

**问题**: 生成速度慢
```bash
# 优化配置
use_float16: true
batch_size: 16               # 4090 可用更大
enable_xformers: true
```

### 5.3 效果优化

**提升自然度**:
1. 使用高质量照片（512x512+，光线均匀）
2. 音频清晰无杂音（16kHz+）
3. 启用人脸增强 `enhance_face: true`
4. 调整 `bbox_shift` 参数

**古诗讲解场景**:
- 选择温和、亲和的教师形象
- 背景简洁，避免杂乱
- 音频语速适中，吐字清晰
- 可添加轻微背景音乐（混音后输入）

## 六、批量处理脚本

### 6.1 批量生成古诗视频

创建 `batch_poems.py`:

```python
import os
import subprocess
from pathlib import Path

# 配置
IMAGE_PATH = "data/image/teacher.png"
AUDIO_DIR = "data/audio/poems"
OUTPUT_DIR = "results/poems"

# 批量处理
audio_files = Path(AUDIO_DIR).glob("*.wav")
for audio_file in audio_files:
    poem_name = audio_file.stem
    output_path = f"{OUTPUT_DIR}/{poem_name}.mp4"
    
    cmd = [
        "python", "inference.py",
        "--image_path", IMAGE_PATH,
        "--audio_path", str(audio_file),
        "--output_path", output_path,
        "--batch_size", "16",
        "--fps", "25"
    ]
    
    print(f"处理: {poem_name}")
    subprocess.run(cmd)
    print(f"完成: {output_path}")
```

### 6.2 监控 GPU 使用

```bash
# 实时监控
watch -n 1 nvidia-smi

# 或使用 Python
pip install gpustat
gpustat -i 1
```

## 七、与现有项目集成

### 7.1 工作流整合

```
1. generate_ppt_video.py  → PPT + 音频 → 带音频的 PPT 视频
2. MuseTalk              → 教师照片 + 音频 → 数字人视频
3. 视频合成工具           → 两个视频 → 最终成品
```

### 7.2 视频合成

使用 FFmpeg 合并:

```bash
# 方式1: 画中画（数字人在角落）
ffmpeg -i ppt_video.mp4 -i teacher_video.mp4 \
  -filter_complex "[1:v]scale=320:240[teacher];[0:v][teacher]overlay=W-w-10:10" \
  -c:a copy output.mp4

# 方式2: 左右分屏
ffmpeg -i ppt_video.mp4 -i teacher_video.mp4 \
  -filter_complex "[0:v][1:v]hstack=inputs=2[v]" \
  -map "[v]" -map 0:a output.mp4

# 方式3: 上下分屏
ffmpeg -i teacher_video.mp4 -i ppt_video.mp4 \
  -filter_complex "[0:v][1:v]vstack=inputs=2[v]" \
  -map "[v]" -map 0:a output.mp4
```

### 7.3 自动化脚本示例

```python
# 完整流程：PPT → PPT视频 → 数字人视频 → 合成
def generate_poem_lesson(poem_name):
    # 1. 生成 PPT 视频
    ppt_video = generate_ppt_video(poem_name)
    
    # 2. 提取音频
    audio = extract_audio(ppt_video)
    
    # 3. 生成数字人视频
    teacher_video = musetalk_inference(
        image="teacher.png",
        audio=audio
    )
    
    # 4. 合成最终视频
    final_video = merge_videos(
        ppt_video, 
        teacher_video,
        layout="pip"  # 画中画
    )
    
    return final_video
```

## 八、性能基准

### 8.1 RTX 4090 性能

| 配置 | 分辨率 | FPS | 生成速度 | 显存占用 |
|-----|--------|-----|----------|----------|
| 低配 | 256x256 | 25 | 0.8x 实时 | 4GB |
| 标准 | 512x512 | 25 | 1.2x 实时 | 6GB |
| 高配 | 512x512 | 30 | 1.0x 实时 | 8GB |
| 极致 | 768x768 | 30 | 0.6x 实时 | 12GB |

**备注**: 
- 1.0x 实时 = 生成 1 分钟视频需要 1 分钟
- 4090 推荐使用"高配"设置

### 8.2 批量处理效率

- 单个 3 分钟古诗讲解: 约 2-3 分钟生成
- 批量 14 首古诗: 约 30-40 分钟完成
- 建议使用批处理脚本 + GPU 监控

## 九、最佳实践

### 9.1 素材准备建议

**教师形象照片**:
- ✅ 正面或微侧面（< 15°）
- ✅ 表情自然、微笑
- ✅ 清晰五官，分辨率 512+
- ✅ 柔和光线，无强阴影
- ❌ 避免夸张表情
- ❌ 避免过度美颜
- ❌ 避免复杂背景

**音频质量**:
- ✅ 清晰无杂音
- ✅ 语速适中（150-180 字/分）
- ✅ 音量适中（-20dB 左右）
- ✅ 16kHz+ 采样率
- ❌ 避免背景音乐过大
- ❌ 避免回音混响

### 9.2 古诗讲解场景优化

1. **人物选择**: 温文尔雅的教师形象，古装或现代装均可
2. **背景**: 纯色或古典书房背景
3. **表情**: 自然、亲切，适当微笑
4. **音频**: 普通话标准，咬字清晰，适当停顿
5. **节奏**: 朗诵部分可稍慢，讲解部分语速正常

### 9.3 生产环境部署

```yaml
# 生产环境配置
server:
  gpu_id: 0
  batch_size: 8
  max_workers: 2           # 并发处理数
  
queue:
  enable: true
  max_queue_size: 100
  timeout: 300
  
cache:
  enable: true
  cache_dir: "cache/"
  ttl: 3600
```

## 十、更新日志

### v1.0 (2024-04)
- 初始版本发布
- 支持单图片 + 音频生成

### v1.1 (2024-06)
- 优化口型同步精度
- 支持批量处理
- 添加 Gradio UI

### v1.2 (2024-09)
- 支持 FP16 加速
- 优化显存占用
- 添加人脸增强选项

## 十一、参考资源

- **官方文档**: https://github.com/TMElyralab/MuseTalk
- **论文**: MuseTalk: Real-Time High Quality Lip Synchronization
- **HuggingFace**: https://huggingface.co/TMElyralab/MuseTalk
- **在线体验**: https://huggingface.co/spaces/TMElyralab/MuseTalk
- **问题反馈**: https://github.com/TMElyralab/MuseTalk/issues

## 十二、技术支持

如遇问题，建议按以下顺序排查:

1. ✅ 检查环境配置（Python、CUDA、PyTorch）
2. ✅ 验证模型权重是否完整下载
3. ✅ 查看官方 Issues 是否有类似问题
4. ✅ 检查输入素材是否符合要求
5. ✅ 尝试降低配置（batch_size、分辨率）
6. ✅ 查看日志文件获取详细错误信息

---

**祝你成功部署 MuseTalk 数字人系统！🎉**
