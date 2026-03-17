"""
测试语音训练服务
"""
import asyncio
from services.voice_training_service import voice_service

async def test_tts():
    """测试TTS功能"""
    print("=" * 50)
    print("测试1: TTS语音合成")
    print("=" * 50)
    
    test_text = "床前明月光，疑是地上霜。"
    
    # 测试女声标准
    print(f"\n生成音频: {test_text}")
    print("音色: 女声-标准, 语速: 正常")
    
    try:
        audio_path = await voice_service.generate_tts_audio(
            text=test_text,
            voice="female_standard",
            rate="normal",
            output_path="static/audio/test_female_standard.mp3"
        )
        print(f"✓ 成功生成音频: {audio_path}")
    except Exception as e:
        print(f"✗ 生成失败: {e}")
    
    # 测试男声快速
    print("\n音色: 男声-标准, 语速: 快速")
    try:
        audio_path = await voice_service.generate_tts_audio(
            text=test_text,
            voice="male_standard",
            rate="fast",
            output_path="static/audio/test_male_fast.mp3"
        )
        print(f"✓ 成功生成音频: {audio_path}")
    except Exception as e:
        print(f"✗ 生成失败: {e}")

def test_asr():
    """测试ASR功能"""
    print("\n" + "=" * 50)
    print("测试2: ASR语音识别")
    print("=" * 50)
    
    # 需要先有音频文件才能测试
    print("\n注意: ASR测试需要先有录音文件")
    print("跳过ASR测试，等待前端录音功能完成后测试")

def test_evaluation():
    """测试发音评估"""
    print("\n" + "=" * 50)
    print("测试3: 发音评估")
    print("=" * 50)
    
    print("\n注意: 发音评估需要用户录音文件")
    print("跳过评估测试，等待前端录音功能完成后测试")

async def main():
    print("\n🎤 语音训练服务测试")
    print("=" * 50)
    
    # 创建必要的目录
    import os
    os.makedirs("static/audio", exist_ok=True)
    
    # 测试TTS
    await test_tts()
    
    # 测试ASR（需要音频文件）
    test_asr()
    
    # 测试评估（需要音频文件）
    test_evaluation()
    
    print("\n" + "=" * 50)
    print("✅ TTS测试完成！")
    print("📁 音频文件保存在: static/audio/")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
