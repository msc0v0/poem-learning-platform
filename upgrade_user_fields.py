"""
升级用户表，添加HSK等级和母语字段
"""
from app import create_app
from models import db, User

def upgrade_user_table():
    """为用户表添加新字段"""
    app = create_app()
    
    with app.app_context():
        # 检查是否需要添加列
        try:
            # 尝试访问新字段，如果失败说明需要添加
            test_query = db.session.query(User.hsk_level).first()
            print("字段已存在，无需升级")
        except Exception as e:
            print(f"需要升级数据库: {e}")
            
            # 使用ALTER TABLE添加新列
            with db.engine.connect() as conn:
                try:
                    # 添加 hsk_level 字段
                    conn.execute(db.text(
                        "ALTER TABLE users ADD COLUMN hsk_level VARCHAR(10) DEFAULT 'HSK3'"
                    ))
                    print("✓ 添加 hsk_level 字段")
                except Exception as e:
                    print(f"hsk_level 字段可能已存在: {e}")
                
                try:
                    # 添加 native_language 字段
                    conn.execute(db.text(
                        "ALTER TABLE users ADD COLUMN native_language VARCHAR(10) DEFAULT 'en'"
                    ))
                    print("✓ 添加 native_language 字段")
                except Exception as e:
                    print(f"native_language 字段可能已存在: {e}")
                
                conn.commit()
            
            print("\n数据库升级完成！")
            
            # 验证升级
            users = User.query.all()
            print(f"\n当前用户数量: {len(users)}")
            for user in users:
                print(f"  - {user.username}: HSK等级={user.hsk_level}, 母语={user.native_language}")

if __name__ == '__main__':
    upgrade_user_table()
