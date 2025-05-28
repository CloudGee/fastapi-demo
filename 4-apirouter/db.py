from sqlmodel import create_engine, Session

engine = create_engine("sqlite:///books.db", echo=True, connect_args={"check_same_thread": False}) # SQLite数据库引擎，echo=True表示打印SQL语句，建议只在测试环境使用这个参数，connect_args={"check_same_thread": False}表示允许多线程访问
def get_db_session():
    """
    获取数据库会话
    """
    with Session(engine) as session:
        yield session
        # 它会返回一个生成器函数，使用with语句可以自动管理数据库连接的打开和关闭
        # 这里的yield语句会在with语句结束时自动关闭数据库连接
        # 这样可以避免手动关闭数据库连接的麻烦
        # yield 是用于“中途返回资源，事后清理资源”的。适合用于数据库连接、文件句柄、网络连接等上下文管理。
        # 这种方式，联合fastAPI的Depends依赖注入，可以在每个请求中自动获取数据库会话。称之为Session Injection。