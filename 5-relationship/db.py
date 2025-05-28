from fastapi import HTTPException, logger
from sqlmodel import create_engine, Session
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps

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

def db_exception_handler(func):
    @wraps(func)
    # 添加wraps可以保留原函数的元数据（如__name__、__doc__等），使得装饰后的函数更像原函数
    def wrapper(*args, **kwargs):
        # 优先从kwargs获取session（这是FastAPI的主要方式）
        session = kwargs.get('session')

        try:
            return func(*args, **kwargs)
        except HTTPException:
            if session:
                session.rollback()
            raise
        except SQLAlchemyError as e:
            if session:
                session.rollback()
            logger.error(f"Database error in {func.__name__}: {str(e)}")
            raise HTTPException(status_code=500, detail="Database operation failed")
        except Exception as e:
            if session:
                session.rollback()
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
    return wrapper