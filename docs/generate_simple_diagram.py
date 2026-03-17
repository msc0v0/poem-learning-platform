"""
简易系统架构图生成工具 - 使用 matplotlib（纯Python，无需外部软件）
运行前需安装: pip install matplotlib
"""

import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端，避免Qt依赖
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.font_manager as fm

def generate_simple_architecture_diagram():
    """使用 matplotlib 生成简易架构图"""
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False
    
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # 定义颜色
    colors = {
        'frontend': '#E3F2FD',
        'backend': '#E8F5E9',
        'service': '#FFF9C4',
        'data': '#FCE4EC',
        'external': '#F3E5F5'
    }
    
    # 标题
    ax.text(7, 9.5, '古诗学习平台系统架构', 
            ha='center', va='center', fontsize=18, fontweight='bold')
    
    # 前端层
    frontend_box = FancyBboxPatch((0.5, 7), 4, 2, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor=colors['frontend'], 
                                  edgecolor='#1976D2', linewidth=2)
    ax.add_patch(frontend_box)
    ax.text(2.5, 8.5, '前端层 (Frontend)', ha='center', fontsize=12, fontweight='bold')
    ax.text(2.5, 8.1, 'HTML5/CSS3/JavaScript', ha='center', fontsize=9)
    ax.text(2.5, 7.7, '页面模块 + 行为追踪', ha='center', fontsize=9)
    ax.text(2.5, 7.3, '原生开发（无框架）', ha='center', fontsize=8, style='italic')
    
    # 后端层
    backend_box = FancyBboxPatch((5.5, 7), 4, 2,
                                 boxstyle="round,pad=0.1",
                                 facecolor=colors['backend'],
                                 edgecolor='#388E3C', linewidth=2)
    ax.add_patch(backend_box)
    ax.text(7.5, 8.5, '后端层 (Backend)', ha='center', fontsize=12, fontweight='bold')
    ax.text(7.5, 8.1, 'Flask 2.3.3', ha='center', fontsize=9)
    ax.text(7.5, 7.7, 'RESTful API + JWT认证', ha='center', fontsize=9)
    ax.text(7.5, 7.3, '9个功能模块', ha='center', fontsize=8, style='italic')
    
    # 外部服务
    external_box = FancyBboxPatch((10, 7), 3.5, 2,
                                  boxstyle="round,pad=0.1",
                                  facecolor=colors['external'],
                                  edgecolor='#7B1FA2', linewidth=2)
    ax.add_patch(external_box)
    ax.text(11.75, 8.5, '外部服务', ha='center', fontsize=12, fontweight='bold')
    ax.text(11.75, 8.1, 'SiliconFlow API', ha='center', fontsize=9)
    ax.text(11.75, 7.7, '(Qwen模型托管)', ha='center', fontsize=8)
    ax.text(11.75, 7.3, 'Edge TTS (微软)', ha='center', fontsize=8)
    
    # 服务层
    service_box1 = FancyBboxPatch((1, 4.5), 3, 1.8,
                                  boxstyle="round,pad=0.1",
                                  facecolor=colors['service'],
                                  edgecolor='#F57C00', linewidth=2)
    ax.add_patch(service_box1)
    ax.text(2.5, 5.8, 'Qwen AI服务', ha='center', fontsize=11, fontweight='bold')
    ax.text(2.5, 5.4, 'Qwen2.5-7B-Instruct', ha='center', fontsize=9)
    ax.text(2.5, 5.0, '中文处理 + 多语言', ha='center', fontsize=8)
    ax.text(2.5, 4.7, 'HSK自适应难度', ha='center', fontsize=8, style='italic')
    
    service_box2 = FancyBboxPatch((5, 4.5), 3, 1.8,
                                  boxstyle="round,pad=0.1",
                                  facecolor=colors['service'],
                                  edgecolor='#F57C00', linewidth=2)
    ax.add_patch(service_box2)
    ax.text(6.5, 5.8, '语音服务', ha='center', fontsize=11, fontweight='bold')
    ax.text(6.5, 5.4, 'TTS: edge-tts', ha='center', fontsize=9)
    ax.text(6.5, 5.0, 'ASR: Whisper', ha='center', fontsize=9)
    ax.text(6.5, 4.7, '音频处理: librosa', ha='center', fontsize=8)
    
    # 数据层
    data_box1 = FancyBboxPatch((9.5, 4.5), 3.5, 1.8,
                               boxstyle="round,pad=0.1",
                               facecolor=colors['data'],
                               edgecolor='#C2185B', linewidth=2)
    ax.add_patch(data_box1)
    ax.text(11.25, 5.8, '数据层 (Data)', ha='center', fontsize=11, fontweight='bold')
    ax.text(11.25, 5.4, 'SQLAlchemy ORM', ha='center', fontsize=9)
    ax.text(11.25, 5.0, 'SQLite 数据库', ha='center', fontsize=9)
    ax.text(11.25, 4.7, '8个核心表', ha='center', fontsize=8, style='italic')
    
    # 数据库表详情
    db_detail_box = FancyBboxPatch((1, 1.5), 12, 2.5,
                                   boxstyle="round,pad=0.1",
                                   facecolor='#FAFAFA',
                                   edgecolor='#757575', linewidth=1.5)
    ax.add_patch(db_detail_box)
    ax.text(7, 3.7, '数据库表结构（8个核心表）', ha='center', fontsize=11, fontweight='bold')
    
    tables = [
        'users (用户信息)',
        'poems (古诗数据)',
        'learning_records (学习记录)',
        'exercises (练习题库)'
    ]
    tables2 = [
        'user_exercise_records (答题记录)',
        'qa_records (AI问答)',
        'attention_tracking (注意力追踪)',
        'learning_session (学习会话)'
    ]
    
    y_pos = 3.2
    for i, table in enumerate(tables):
        ax.text(3.5, y_pos - i*0.35, f'• {table}', ha='left', fontsize=8)
    
    for i, table in enumerate(tables2):
        ax.text(8.5, y_pos - i*0.35, f'• {table}', ha='left', fontsize=8)
    
    # 技术栈说明
    tech_box = FancyBboxPatch((1, 0.2), 12, 1,
                              boxstyle="round,pad=0.05",
                              facecolor='#E0F7FA',
                              edgecolor='#0097A7', linewidth=1.5)
    ax.add_patch(tech_box)
    ax.text(7, 0.9, '核心技术栈', ha='center', fontsize=10, fontweight='bold')
    ax.text(7, 0.6, 'Flask + SQLAlchemy + SQLite | Qwen2.5-7B (SiliconFlow) | edge-tts + Whisper | 原生 JavaScript',
            ha='center', fontsize=8)
    ax.text(7, 0.35, '轻量化架构 • 高性价比 • 中文优化 • 多语言支持 • 学习行为追踪',
            ha='center', fontsize=7, style='italic', color='#00695C')
    
    # 绘制箭头连接
    arrows = [
        ((4.5, 8), (5.5, 8), 'HTTP/AJAX'),
        ((7.5, 7), (2.5, 6.3), 'AI问答'),
        ((7.5, 7), (6.5, 6.3), '语音处理'),
        ((9.5, 8), (11.75, 8), 'API调用'),
        ((9.5, 5.4), (11.25, 5.4), '数据操作'),
        ((2.5, 4.5), (11.75, 7), 'Qwen API'),
        ((6.5, 4.5), (11.75, 7.5), 'TTS API'),
    ]
    
    for start, end, label in arrows:
        arrow = FancyArrowPatch(start, end,
                               arrowstyle='->', mutation_scale=20,
                               color='#546E7A', linewidth=1.5,
                               linestyle='--', alpha=0.7)
        ax.add_patch(arrow)
        mid_x, mid_y = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
        ax.text(mid_x, mid_y, label, fontsize=7, 
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='none'))
    
    plt.tight_layout()
    output_path = 'e:/poem_project/code/docs/system_architecture_simple.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ 系统架构图已生成: {output_path}")
    plt.close()
    
    return output_path

if __name__ == '__main__':
    try:
        generate_simple_architecture_diagram()
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        print("\n请先安装 matplotlib:")
        print("  pip install matplotlib")
