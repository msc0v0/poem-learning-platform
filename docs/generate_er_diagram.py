"""
数据库ER图生成工具
从 SQLite 数据库读取表结构并生成ER图
运行前需安装: pip install graphviz
"""

import sqlite3
from graphviz import Digraph

def get_table_info(db_path):
    """从SQLite数据库获取表结构信息"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    table_info = {}
    for table in tables:
        # 获取表的列信息
        cursor.execute(f"PRAGMA table_info({table});")
        columns = cursor.fetchall()
        
        # 获取外键信息
        cursor.execute(f"PRAGMA foreign_key_list({table});")
        foreign_keys = cursor.fetchall()
        
        table_info[table] = {
            'columns': columns,
            'foreign_keys': foreign_keys
        }
    
    conn.close()
    return table_info

def generate_er_diagram(db_path='e:/poem_project/code/instance/poem_platform.db'):
    """生成ER图"""
    dot = Digraph(comment='古诗学习平台数据库ER图', format='png')
    dot.attr(rankdir='TB')
    dot.attr('node', shape='record', fontname='Microsoft YaHei')
    dot.attr('edge', fontname='Microsoft YaHei', fontsize='10')
    
    # 获取数据库表信息
    try:
        table_info = get_table_info(db_path)
    except Exception as e:
        print(f"❌ 读取数据库失败: {e}")
        return None
    
    # 为每个表创建节点
    for table_name, info in table_info.items():
        columns = info['columns']
        
        # 构建表的字段列表
        fields = []
        for col in columns:
            col_id, col_name, col_type, not_null, default_val, pk = col
            
            # 标记主键
            if pk:
                fields.append(f"<{col_name}> 🔑 {col_name}: {col_type}")
            else:
                fields.append(f"<{col_name}> {col_name}: {col_type}")
        
        # 创建表节点
        label = f"{{{table_name}|{'|'.join(fields)}}}"
        dot.node(table_name, label, style='filled', fillcolor='lightblue')
    
    # 添加外键关系
    relationships = []
    for table_name, info in table_info.items():
        for fk in info['foreign_keys']:
            fk_id, seq, ref_table, from_col, to_col, on_update, on_delete, match = fk
            relationships.append({
                'from_table': table_name,
                'from_col': from_col,
                'to_table': ref_table,
                'to_col': to_col
            })
    
    # 绘制关系线
    for rel in relationships:
        from_port = f"{rel['from_table']}:{rel['from_col']}"
        to_port = f"{rel['to_table']}:{rel['to_col']}"
        label = f"{rel['from_col']} → {rel['to_col']}"
        dot.edge(from_port, to_port, label=label, color='red', arrowhead='crow')
    
    # 保存
    output_path = 'e:/poem_project/code/docs/database_er_diagram'
    dot.render(output_path, view=False, cleanup=True)
    print(f"✅ 数据库ER图已生成: {output_path}.png")
    print(f"\n📊 数据库统计:")
    print(f"  • 总表数: {len(table_info)}")
    print(f"  • 外键关系: {len(relationships)}")
    print(f"\n📋 表列表:")
    for table_name, info in table_info.items():
        print(f"  • {table_name}: {len(info['columns'])} 个字段")
    
    return f"{output_path}.png"

if __name__ == '__main__':
    try:
        generate_er_diagram()
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        print("\n请先安装 graphviz:")
        print("  pip install graphviz")
        print("  并安装 Graphviz 软件: https://graphviz.org/download/")
