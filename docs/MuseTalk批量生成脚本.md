# MuseTalk 批量生成数字人视频脚本

## 一、准备数据

### 1.1 目录结构

```
~/MuseTalk/
├── data/
│   ├── image/
│   │   └── teacher.png          # 教师照片（共用）
│   └── audio/
│       ├── 春晓_讲解.wav
│       ├── 咏鹅_讲解.wav
│       ├── 悯农_讲解.wav
│       └── ...                  # 更多古诗音频
├── results/                     # 输出目录
└── batch_generate.py           # 批量处理脚本
```

### 1.2 准备教师照片

```bash
cd ~/MuseTalk
mkdir -p data/image
# 上传 teacher.png 到 data/image/
```

### 1.3 准备音频文件

```bash
mkdir -p data/audio

# 从你的项目复制音频（如果已有）
# 或者重新生成
```

---

## 二、批量处理脚本

### 方式1：Python 批量脚本（推荐）

创建 `~/MuseTalk/batch_generate.py`:

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MuseTalk 批量生成数字人视频
用于古诗讲解场景
"""

import os
import subprocess
import time
from pathlib import Path

# ==================== 配置区 ====================

# 教师照片路径
TEACHER_IMAGE = "data/image/teacher.png"

# 音频文件目录
AUDIO_DIR = "data/audio"

# 输出目录
OUTPUT_DIR = "results/poems"

# 生成参数
FPS = 25
BATCH_SIZE = 16  # 4090 推荐 16，显存小用 8
BBOX_SHIFT = 0

# 是否使用 FP16 加速
USE_FP16 = True

# ================================================


def check_environment():
    """检查环境"""
    print("=" * 60)
    print("检查环境...")
    print("=" * 60)
    
    # 检查图片
    if not os.path.exists(TEACHER_IMAGE):
        print(f"❌ 教师照片不存在: {TEACHER_IMAGE}")
        print("请将教师照片放到 data/image/teacher.png")
        return False
    print(f"✓ 教师照片: {TEACHER_IMAGE}")
    
    # 检查音频目录
    if not os.path.exists(AUDIO_DIR):
        print(f"❌ 音频目录不存在: {AUDIO_DIR}")
        return False
    
    # 获取音频列表
    audio_files = list(Path(AUDIO_DIR).glob("*.wav")) + \
                  list(Path(AUDIO_DIR).glob("*.mp3"))
    
    if not audio_files:
        print(f"❌ 音频目录为空: {AUDIO_DIR}")
        return False
    
    print(f"✓ 找到 {len(audio_files)} 个音频文件")
    
    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"✓ 输出目录: {OUTPUT_DIR}")
    
    return True


def get_audio_files():
    """获取所有音频文件"""
    audio_files = []
    
    # WAV 文件
    audio_files.extend(Path(AUDIO_DIR).glob("*.wav"))
    
    # MP3 文件
    audio_files.extend(Path(AUDIO_DIR).glob("*.mp3"))
    
    # 排序
    audio_files.sort()
    
    return audio_files


def generate_video(audio_path, output_path):
    """生成单个视频"""
    cmd = [
        "python", "inference_cli.py",
        "--image_path", TEACHER_IMAGE,
        "--audio_path", str(audio_path),
        "--result_dir", OUTPUT_DIR,
        "--fps", str(FPS),
        "--batch_size", str(BATCH_SIZE),
        "--bbox_shift", str(BBOX_SHIFT)
    ]
    
    if USE_FP16:
        cmd.extend(["--use_float16", "True"])
    
    print(f"\n执行命令:")
    print(" ".join(cmd))
    print()
    
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=False,
            text=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 生成失败: {e}")
        return False


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("MuseTalk 批量生成数字人视频")
    print("=" * 60 + "\n")
    
    # 检查环境
    if not check_environment():
        return
    
    # 获取音频列表
    audio_files = get_audio_files()
    total = len(audio_files)
    
    print("\n" + "=" * 60)
    print(f"开始批量生成 {total} 个视频")
    print("=" * 60 + "\n")
    
    # 统计信息
    success_count = 0
    failed_count = 0
    failed_list = []
    
    start_time = time.time()
    
    # 逐个处理
    for idx, audio_path in enumerate(audio_files, 1):
        poem_name = audio_path.stem  # 不含扩展名的文件名
        output_path = f"{OUTPUT_DIR}/{poem_name}.mp4"
        
        print("=" * 60)
        print(f"[{idx}/{total}] 处理: {poem_name}")
        print("=" * 60)
        print(f"音频: {audio_path}")
        print(f"输出: {output_path}")
        
        # 检查是否已存在
        if os.path.exists(output_path):
            print(f"⚠️  视频已存在，跳过: {output_path}")
            success_count += 1
            continue
        
        # 生成视频
        if generate_video(audio_path, output_path):
            success_count += 1
            print(f"✓ 完成: {poem_name}")
        else:
            failed_count += 1
            failed_list.append(poem_name)
            print(f"✗ 失败: {poem_name}")
    
    # 总结
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 60)
    print("批量生成完成")
    print("=" * 60)
    print(f"总数: {total}")
    print(f"成功: {success_count}")
    print(f"失败: {failed_count}")
    print(f"耗时: {elapsed_time/60:.2f} 分钟")
    
    if failed_list:
        print("\n失败列表:")
        for name in failed_list:
            print(f"  - {name}")
    
    print(f"\n输出目录: {OUTPUT_DIR}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
```

---

### 方式2：Shell 批量脚本

创建 `~/MuseTalk/batch_generate.sh`:

```bash
#!/bin/bash

# 配置
TEACHER_IMAGE="data/image/teacher.png"
AUDIO_DIR="data/audio"
OUTPUT_DIR="results/poems"
FPS=25
BATCH_SIZE=16

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 统计
total=0
success=0
failed=0

# 遍历音频文件
for audio in "$AUDIO_DIR"/*.{wav,mp3}; do
    # 检查文件是否存在
    [ -e "$audio" ] || continue
    
    # 获取文件名（不含路径和扩展名）
    filename=$(basename "$audio")
    poem_name="${filename%.*}"
    output_path="$OUTPUT_DIR/${poem_name}.mp4"
    
    total=$((total + 1))
    
    echo "========================================"
    echo "[$total] 处理: $poem_name"
    echo "========================================"
    
    # 检查是否已存在
    if [ -f "$output_path" ]; then
        echo "⚠️  视频已存在，跳过"
        success=$((success + 1))
        continue
    fi
    
    # 生成视频
    python inference_cli.py \
        --image_path "$TEACHER_IMAGE" \
        --audio_path "$audio" \
        --result_dir "$OUTPUT_DIR" \
        --fps "$FPS" \
        --batch_size "$BATCH_SIZE"
    
    if [ $? -eq 0 ]; then
        echo "✓ 完成: $poem_name"
        success=$((success + 1))
    else
        echo "✗ 失败: $poem_name"
        failed=$((failed + 1))
    fi
done

# 总结
echo ""
echo "========================================"
echo "批量生成完成"
echo "========================================"
echo "总数: $total"
echo "成功: $success"
echo "失败: $failed"
echo "输出目录: $OUTPUT_DIR"
```

---

## 三、使用方法

### 3.1 运行 Python 脚本

```bash
cd ~/MuseTalk

# 给脚本添加执行权限（可选）
chmod +x batch_generate.py

# 运行
python batch_generate.py
```

### 3.2 运行 Shell 脚本

```bash
cd ~/MuseTalk

# 添加执行权限
chmod +x batch_generate.sh

# 运行
./batch_generate.sh
```

---

## 四、高级功能

### 4.1 指定古诗列表

修改脚本，只处理指定的古诗：

```python
# 在 batch_generate.py 中添加

POEM_LIST = [
    "春晓",
    "咏鹅",
    "悯农",
    "静夜思",
    "登鹳雀楼"
]

def get_audio_files():
    """获取指定的音频文件"""
    audio_files = []
    for poem in POEM_LIST:
        # 尝试不同扩展名
        for ext in ['.wav', '.mp3']:
            audio_path = Path(AUDIO_DIR) / f"{poem}_讲解{ext}"
            if audio_path.exists():
                audio_files.append(audio_path)
                break
    return audio_files
```

### 4.2 并行处理（加速）

```python
from concurrent.futures import ProcessPoolExecutor, as_completed

def batch_generate_parallel(audio_files, max_workers=2):
    """并行生成（注意GPU显存）"""
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(generate_video, audio, None): audio 
            for audio in audio_files
        }
        
        for future in as_completed(futures):
            audio = futures[future]
            try:
                future.result()
                print(f"✓ {audio.stem}")
            except Exception as e:
                print(f"✗ {audio.stem}: {e}")
```

### 4.3 断点续传

脚本已支持！如果视频已存在，会自动跳过。

---

## 五、监控与优化

### 5.1 实时监控 GPU

```bash
# 终端1: 运行批量生成
python batch_generate.py

# 终端2: 监控 GPU
watch -n 1 nvidia-smi
```

### 5.2 日志记录

```python
import logging

# 配置日志
logging.basicConfig(
    filename='batch_generate.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 记录日志
logging.info(f"开始生成: {poem_name}")
```

---

## 六、性能参考

### 4090 批量生成性能

| 配置 | 单个视频时长 | 生成时间 | 14首古诗总耗时 |
|------|-------------|----------|----------------|
| 标准 (batch_size=16) | 3分钟 | 2-3分钟 | ~35分钟 |
| 快速 (batch_size=8) | 3分钟 | 3-4分钟 | ~45分钟 |
| 高质 (batch_size=16, fp16) | 3分钟 | 2分钟 | ~28分钟 |

---

## 七、常见问题

### Q1: 中途失败怎么办？
**A**: 重新运行脚本，已完成的会自动跳过。

### Q2: 如何加速？
**A**: 
- 增大 `batch_size` (4090 可用 16-24)
- 启用 `use_float16=True`
- 降低 `fps` (25 → 20)

### Q3: 显存不足？
**A**: 
- 减小 `batch_size` (16 → 8 → 4)
- 降低分辨率
- 单进程处理（不要并行）

---

## 八、完整工作流

```bash
# 1. 准备数据
cd ~/MuseTalk
mkdir -p data/image data/audio results/poems

# 2. 上传教师照片
# data/image/teacher.png

# 3. 准备音频文件
# data/audio/春晓_讲解.wav
# data/audio/咏鹅_讲解.wav
# ...

# 4. 运行批量生成
python batch_generate.py

# 5. 查看结果
ls -lh results/poems/
```

---

**批量生成完成后，所有数字人视频都在 `results/poems/` 目录！**
