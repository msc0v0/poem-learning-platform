"""
批量生成所有古诗的TTS音频
为每首诗生成4种音色 x 3种语速 = 12个音频文件
"""
import asyncio
import os
import sys
from services.voice_training_service import voice_service
from models import db
from models.poem import Poem
from app import create_app

# 音色配置（移除不稳定的female_gentle）
VOICES = {
    'female_standard': '女声-标准',
    'male_standard': '男声-标准',
    'male_energetic': '男声-活力'
}

# 语速配置
RATES = {
    'slow': '慢速',
    'normal': '正常',
    'fast': '快速'
}

async def generate_poem_audio(poem, voice_id, rate_id, output_dir):
    """
    为单首诗生成音频
    """
    # 构建完整文本：标题 + 作者 + 朝代 + 诗文
    full_text = f"{poem.title}，{poem.dynasty}{poem.author}。{poem.content}"
    
    # 文件命名：诗ID_音色_语速.mp3
    filename = f"{poem.id:02d}_{voice_id}_{rate_id}.mp3"
    output_path = os.path.join(output_dir, filename)
    
    # 如果文件已存在，跳过
    if os.path.exists(output_path):
        print(f"  ⏭️  已存在: {filename}")
        return True
    
    try:
        # 生成音频
        await voice_service.generate_tts_audio(
            text=full_text,
            voice=voice_id,
            rate=rate_id,
            output_path=output_path
        )
        print(f"  ✓ 生成成功: {filename}")
        return True
    except Exception as e:
        print(f"  ✗ 生成失败: {filename} - {e}")
        return False

async def batch_generate_all():
    """
    批量生成所有古诗的TTS音频
    """
    print("\n" + "=" * 70)
    print("🎤 批量生成古诗TTS音频")
    print("=" * 70)
    
    # 创建Flask应用上下文
    app = create_app()
    
    with app.app_context():
        # 获取所有古诗
        poems = Poem.query.order_by(Poem.id).all()
        total_poems = len(poems)
        
        if total_poems == 0:
            print("❌ 数据库中没有古诗数据")
            return
        
        print(f"\n📚 找到 {total_poems} 首古诗")
        print(f"🎵 每首诗生成 {len(VOICES)} 种音色 × {len(RATES)} 种语速 = {len(VOICES) * len(RATES)} 个音频")
        print(f"📊 总计需要生成: {total_poems * len(VOICES) * len(RATES)} 个音频文件")
        
        # 创建输出目录
        output_dir = "static/audio/poems"
        os.makedirs(output_dir, exist_ok=True)
        print(f"📁 输出目录: {output_dir}\n")
        
        # 统计
        success_count = 0
        skip_count = 0
        fail_count = 0
        
        # 遍历每首诗
        for idx, poem in enumerate(poems, 1):
            print(f"\n[{idx}/{total_poems}] 📖 {poem.title} - {poem.author}")
            print("-" * 70)
            
            # 遍历每种音色和语速组合
            for voice_id, voice_name in VOICES.items():
                for rate_id, rate_name in RATES.items():
                    result = await generate_poem_audio(poem, voice_id, rate_id, output_dir)
                    
                    if result:
                        # 检查是否是跳过的
                        filename = f"{poem.id:02d}_{voice_id}_{rate_id}.mp3"
                        if os.path.exists(os.path.join(output_dir, filename)):
                            skip_count += 1
                        else:
                            success_count += 1
                    else:
                        fail_count += 1
                    
                    # 短暂延迟，避免请求过快
                    await asyncio.sleep(0.1)
        
        # 输出统计
        print("\n" + "=" * 70)
        print("📊 生成统计")
        print("=" * 70)
        print(f"✅ 新生成: {success_count} 个")
        print(f"⏭️  已跳过: {skip_count} 个（文件已存在）")
        print(f"❌ 失败: {fail_count} 个")
        print(f"📁 保存位置: {os.path.abspath(output_dir)}")
        print("=" * 70)

async def generate_single_poem(poem_id: int):
    """
    为单首诗生成所有音频
    """
    print("\n" + "=" * 70)
    print(f"🎤 为诗ID={poem_id}生成TTS音频")
    print("=" * 70)
    
    app = create_app()
    
    with app.app_context():
        poem = Poem.query.get(poem_id)
        
        if not poem:
            print(f"❌ 未找到ID为 {poem_id} 的古诗")
            return
        
        print(f"\n📖 {poem.title} - {poem.author}")
        print(f"📝 内容: {poem.content[:30]}...")
        
        # 创建输出目录
        output_dir = "static/audio/poems"
        os.makedirs(output_dir, exist_ok=True)
        
        success = 0
        total = len(VOICES) * len(RATES)
        
        for voice_id, voice_name in VOICES.items():
            for rate_id, rate_name in RATES.items():
                print(f"\n生成: {voice_name} - {rate_name}")
                result = await generate_poem_audio(poem, voice_id, rate_id, output_dir)
                if result:
                    success += 1
                await asyncio.sleep(0.1)
        
        print("\n" + "=" * 70)
        print(f"✅ 完成: {success}/{total}")
        print("=" * 70)

async def list_generated_files():
    """
    列出已生成的音频文件
    """
    output_dir = "static/audio/poems"
    
    if not os.path.exists(output_dir):
        print(f"❌ 目录不存在: {output_dir}")
        return
    
    files = [f for f in os.listdir(output_dir) if f.endswith('.mp3')]
    files.sort()
    
    print("\n" + "=" * 70)
    print(f"📁 已生成的音频文件 ({len(files)} 个)")
    print("=" * 70)
    
    # 按诗ID分组
    app = create_app()
    with app.app_context():
        poems = Poem.query.order_by(Poem.id).all()
        
        for poem in poems:
            poem_files = [f for f in files if f.startswith(f"{poem.id:02d}_")]
            if poem_files:
                print(f"\n📖 [{poem.id:02d}] {poem.title}")
                print(f"   共 {len(poem_files)} 个音频:")
                for f in poem_files:
                    size_kb = os.path.getsize(os.path.join(output_dir, f)) / 1024
                    print(f"   - {f} ({size_kb:.1f} KB)")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='批量生成古诗TTS音频')
    parser.add_argument('--all', action='store_true', help='生成所有古诗的音频')
    parser.add_argument('--poem', type=int, help='生成指定ID古诗的音频')
    parser.add_argument('--list', action='store_true', help='列出已生成的音频')
    
    args = parser.parse_args()
    
    if args.list:
        asyncio.run(list_generated_files())
    elif args.poem:
        asyncio.run(generate_single_poem(args.poem))
    elif args.all:
        asyncio.run(batch_generate_all())
    else:
        print("\n使用说明:")
        print("  python batch_generate_tts.py --all          # 生成所有古诗")
        print("  python batch_generate_tts.py --poem 1       # 生成指定古诗")
        print("  python batch_generate_tts.py --list         # 列出已生成文件")

if __name__ == "__main__":
    main()
