"""
系统架构图生成工具
使用 Graphviz 生成系统架构图
运行前需安装: pip install graphviz
"""

from graphviz import Digraph

def generate_architecture_diagram():
    """生成系统架构图"""
    dot = Digraph(comment='古诗学习平台系统架构', format='png')
    dot.attr(rankdir='TB', splines='ortho')
    dot.attr('node', shape='box', style='rounded,filled', fontname='Microsoft YaHei')
    
    # 前端层
    with dot.subgraph(name='cluster_frontend') as c:
        c.attr(label='前端层 (Frontend)', style='filled', color='lightblue')
        c.node('html', 'HTML5/CSS3/JavaScript\n(原生开发)', fillcolor='lightcyan')
        c.node('pages', '页面模块\n• 古诗列表\n• 学习页面\n• 练习系统\n• 仪表板', fillcolor='lightcyan')
        c.node('tracking', '前端追踪\n• 鼠标行为\n• 注意力分析\n• 交互事件', fillcolor='lightcyan')
    
    # 后端层
    with dot.subgraph(name='cluster_backend') as c:
        c.attr(label='后端层 (Backend - Flask)', style='filled', color='lightgreen')
        c.node('flask', 'Flask 2.3.3\nRESTful API', fillcolor='lightgreen')
        c.node('auth', '认证模块\nJWT + Bcrypt', fillcolor='palegreen')
        c.node('routes', 'API路由\n• /api/poems\n• /api/learning\n• /api/exercises\n• /api/ai\n• /api/tracking', fillcolor='palegreen')
    
    # 服务层
    with dot.subgraph(name='cluster_services') as c:
        c.attr(label='服务层 (Services)', style='filled', color='lightyellow')
        c.node('qwen', 'Qwen AI服务\nQwen2.5-7B-Instruct\n(SiliconFlow API)', fillcolor='yellow')
        c.node('tts', '语音服务\n• TTS: edge-tts\n• ASR: Whisper\n• 音频处理: librosa', fillcolor='yellow')
    
    # 数据层
    with dot.subgraph(name='cluster_data') as c:
        c.attr(label='数据层 (Data)', style='filled', color='lightpink')
        c.node('orm', 'SQLAlchemy ORM', fillcolor='pink')
        c.node('db', 'SQLite数据库\npoem_platform.db\n8个核心表', fillcolor='pink')
    
    # 外部服务
    with dot.subgraph(name='cluster_external') as c:
        c.attr(label='外部服务', style='filled', color='lavender')
        c.node('siliconflow', 'SiliconFlow API\n(Qwen模型托管)', fillcolor='lavender')
        c.node('edge_tts_api', 'Edge TTS\n(微软免费TTS)', fillcolor='lavender')
    
    # 连接关系
    dot.edge('html', 'pages')
    dot.edge('pages', 'tracking')
    dot.edge('pages', 'flask', label='HTTP/AJAX')
    dot.edge('tracking', 'flask', label='行为数据')
    
    dot.edge('flask', 'auth')
    dot.edge('flask', 'routes')
    dot.edge('routes', 'qwen', label='AI问答')
    dot.edge('routes', 'tts', label='语音处理')
    dot.edge('routes', 'orm', label='数据操作')
    
    dot.edge('qwen', 'siliconflow', label='API调用')
    dot.edge('tts', 'edge_tts_api', label='TTS生成')
    
    dot.edge('orm', 'db')
    
    # 保存
    output_path = 'e:/poem_project/code/docs/system_architecture'
    dot.render(output_path, view=False, cleanup=True)
    print(f"✅ 系统架构图已生成: {output_path}.png")
    return f"{output_path}.png"

if __name__ == '__main__':
    try:
        generate_architecture_diagram()
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        print("\n请先安装 graphviz:")
        print("  pip install graphviz")
        print("  并安装 Graphviz 软件: https://graphviz.org/download/")
