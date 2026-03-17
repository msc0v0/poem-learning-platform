"""
数据库ER图生成工具 v2 - 使用 matplotlib（纯Python，无需Graphviz）
运行前需安装: pip install matplotlib
"""

import sqlite3
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端，避免Qt依赖
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

def get_table_info(db_path):
    """从SQLite数据库获取表结构信息"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    table_info = {}
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table});")
        columns = cursor.fetchall()
        
        cursor.execute(f"PRAGMA foreign_key_list({table});")
        foreign_keys = cursor.fetchall()
        
        table_info[table] = {
            'columns': columns,
            'foreign_keys': foreign_keys
        }
    
    conn.close()
    return table_info

def generate_er_diagram_simple(db_path='e:/poem_project/code/instance/poem_platform.db'):
    """使用 matplotlib 生成ER图"""
    
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False
    
    try:
        table_info = get_table_info(db_path)
    except Exception as e:
        print(f"❌ 读取数据库失败: {e}")
        return None
    
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # 标题
    ax.text(8, 11.5, '古诗学习平台数据库 E-R 图', 
            ha='center', va='center', fontsize=18, fontweight='bold')
    
    # 表的位置布局（手动调整以获得更好的视觉效果）
    table_positions = {
        'users': (2, 9),
        'poems': (8, 9),
        'learning_records': (2, 6.5),
        'exercises': (8, 6.5),
        'user_exercise_records': (5, 4.5),
        'qa_records': (11, 6.5),
        'attention_tracking': (14, 9),
        'learning_session': (2, 2.5),
        'interaction_event': (8, 2.5)
    }
    
    colors = {
        'users': '#E3F2FD',
        'poems': '#FFF9C4',
        'learning_records': '#E8F5E9',
        'exercises': '#FCE4EC',
        'user_exercise_records': '#F3E5F5',
        'qa_records': '#FFE0B2',
        'attention_tracking': '#FFCCBC',
        'learning_session': '#C8E6C9',
        'interaction_event': '#D1C4E9'
    }
    
    # 绘制表
    for table_name, (x, y) in table_positions.items():
        if table_name not in table_info:
            continue
            
        columns = table_info[table_name]['columns']
        
        # 计算表框高度
        box_height = 0.3 + len(columns) * 0.2
        box_width = 2.5
        
        # 绘制表框
        color = colors.get(table_name, '#F5F5F5')
        table_box = FancyBboxPatch((x - box_width/2, y - box_height/2), 
                                   box_width, box_height,
                                   boxstyle="round,pad=0.05",
                                   facecolor=color,
                                   edgecolor='#424242', linewidth=2)
        ax.add_patch(table_box)
        
        # 表名
        ax.text(x, y + box_height/2 - 0.15, table_name, 
                ha='center', fontsize=10, fontweight='bold')
        
        # 绘制分隔线
        ax.plot([x - box_width/2, x + box_width/2], 
                [y + box_height/2 - 0.3, y + box_height/2 - 0.3],
                'k-', linewidth=1)
        
        # 字段列表（只显示前6个字段）
        y_offset = y + box_height/2 - 0.5
        for i, col in enumerate(columns[:6]):
            col_id, col_name, col_type, not_null, default_val, pk = col
            
            # 主键标记
            prefix = '🔑 ' if pk else '   '
            field_text = f"{prefix}{col_name}"
            
            ax.text(x - box_width/2 + 0.1, y_offset, field_text,
                   ha='left', fontsize=7, family='monospace')
            y_offset -= 0.2
        
        if len(columns) > 6:
            ax.text(x, y_offset, '...', ha='center', fontsize=7, style='italic')
    
    # 绘制外键关系
    relationships = []
    for table_name, info in table_info.items():
        for fk in info['foreign_keys']:
            fk_id, seq, ref_table, from_col, to_col, on_update, on_delete, match = fk
            if table_name in table_positions and ref_table in table_positions:
                relationships.append({
                    'from': table_name,
                    'to': ref_table,
                    'label': f"{from_col}→{to_col}"
                })
    
    # 绘制关系箭头
    for rel in relationships:
        from_pos = table_positions[rel['from']]
        to_pos = table_positions[rel['to']]
        
        arrow = FancyArrowPatch(from_pos, to_pos,
                               arrowstyle='->', mutation_scale=15,
                               color='#D32F2F', linewidth=1.5,
                               linestyle='--', alpha=0.6,
                               connectionstyle="arc3,rad=0.2")
        ax.add_patch(arrow)
    
    # 图例
    legend_y = 0.8
    ax.text(1, legend_y, '图例说明:', fontsize=10, fontweight='bold')
    ax.text(1, legend_y - 0.3, '🔑 = 主键 (Primary Key)', fontsize=8)
    ax.text(1, legend_y - 0.5, '红色虚线箭头 = 外键关系 (Foreign Key)', fontsize=8)
    
    # 统计信息
    stats_text = f"总表数: {len(table_info)} | 外键关系: {len(relationships)}"
    ax.text(8, 0.3, stats_text, ha='center', fontsize=9,
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#E0F7FA', edgecolor='#0097A7'))
    
    plt.tight_layout()
    output_path = 'e:/poem_project/code/docs/database_er_diagram_simple.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ 数据库ER图已生成: {output_path}")
    print(f"\n📊 数据库统计:")
    print(f"  • 总表数: {len(table_info)}")
    print(f"  • 外键关系: {len(relationships)}")
    print(f"\n📋 表列表:")
    for table_name, info in table_info.items():
        print(f"  • {table_name}: {len(info['columns'])} 个字段")
    
    plt.close()
    return output_path

if __name__ == '__main__':
    try:
        generate_er_diagram_simple()
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        print("\n请先安装 matplotlib:")
        print("  pip install matplotlib")
