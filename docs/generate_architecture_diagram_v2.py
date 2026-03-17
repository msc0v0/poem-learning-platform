"""
系统架构图生成工具 v2 - 使用 diagrams 库（无需 Graphviz）
运行前需安装: pip install diagrams
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.custom import Custom
from diagrams.programming.language import Python
from diagrams.onprem.database import SQLite
from diagrams.onprem.client import Client
from diagrams.saas import Chat

def generate_architecture_diagram():
    """生成系统架构图 - 使用 diagrams 库"""
    
    graph_attr = {
        "fontsize": "14",
        "fontname": "Microsoft YaHei",
        "bgcolor": "white",
        "pad": "0.5"
    }
    
    with Diagram("古诗学习平台系统架构", 
                 filename="e:/poem_project/code/docs/system_architecture_v2",
                 show=False,
                 direction="TB",
                 graph_attr=graph_attr):
        
        # 前端层
        with Cluster("前端层 (Frontend)"):
            frontend = Client("HTML5/CSS3/JavaScript\n原生开发")
            pages = Client("页面模块\n古诗列表/学习页面\n练习系统/仪表板")
            tracking = Client("前端追踪\n鼠标行为/注意力分析")
            
            frontend >> pages >> tracking
        
        # 后端层
        with Cluster("后端层 (Backend)"):
            flask = Python("Flask 2.3.3\nRESTful API")
            auth = Python("JWT + Bcrypt\n身份认证")
            routes = Python("API路由\n9个功能模块")
            
            flask >> auth
            flask >> routes
        
        # 服务层
        with Cluster("服务层 (Services)"):
            qwen = Chat("Qwen AI服务\nQwen2.5-7B-Instruct")
            tts = Python("语音服务\nTTS + ASR + 音频处理")
        
        # 数据层
        with Cluster("数据层 (Data)"):
            orm = Python("SQLAlchemy ORM")
            db = SQLite("SQLite数据库\npoem_platform.db\n8个核心表")
            
            orm >> db
        
        # 外部服务
        with Cluster("外部服务"):
            siliconflow = Chat("SiliconFlow API\nQwen模型托管")
            edge_tts = Chat("Edge TTS\n微软免费TTS")
        
        # 连接关系
        tracking >> Edge(label="HTTP/AJAX") >> flask
        flask >> Edge(label="AI问答") >> qwen
        flask >> Edge(label="语音处理") >> tts
        flask >> Edge(label="数据操作") >> orm
        
        qwen >> Edge(label="API调用") >> siliconflow
        tts >> Edge(label="TTS生成") >> edge_tts
    
    print("✅ 系统架构图已生成: e:/poem_project/code/docs/system_architecture_v2.png")
    return "e:/poem_project/code/docs/system_architecture_v2.png"

if __name__ == '__main__':
    try:
        generate_architecture_diagram()
    except ImportError as e:
        print(f"❌ 缺少依赖库: {e}")
        print("\n请安装 diagrams 库:")
        print("  pip install diagrams")
    except Exception as e:
        print(f"❌ 生成失败: {e}")
