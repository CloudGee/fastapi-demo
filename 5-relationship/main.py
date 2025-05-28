from fastapi import FastAPI
from sqlmodel import create_engine, SQLModel, Session
from routers import book, author  # 导入自定义的路由模块
from db import engine
import uvicorn


# # 它会在所有其它代码执行之前运行一次，这是一个即将被弃用的功能
# @app.on_event("startup")
# def on_startup():
#     SQLModel.metadata.create_all(engine)  # 创建数据库表
# 不需要在FastAPI定义的时候声明。
# ================================================================
# 新方式如下：
# 需要在FastAPI定义的时候声明。如 app = FastAPI(title="Book API", description="Book API", version="1.0.0", lifespan=lifespan)
from contextlib import asynccontextmanager
@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield
    pass

app = FastAPI(title="Book API", description="Book API", version="1.0.0", lifespan=lifespan)

app.include_router(book.router)  # 将书籍相关的路由添加到FastAPI应用中
app.include_router(author.router)  # 将作者相关的路由添加到FastAPI应用中


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8008, reload=True)  # 启动FastAPI应用，reload=True表示代码修改后自动重启

# session.get() vs select() 区别：

# 1. 主键限制：
#   - session.get() 只能用主键查询
#   - select() 可以用任意字段查询

# 2. 缓存机制：
#   - session.get() 优先从缓存取，性能更好
#   - select() 每次都查数据库

# 3. 代码复杂度：
#   - session.get(Book, id) 简洁
#   - select(Book).where(Book.id_ == value) 复杂

# 4. 使用场景：
#   - 主键查询单个对象 → 用 session.get()
#   - 复杂查询/非主键查询 → 用 select()

# 示例：
# # 主键查询
# book = session.get(Book, book_id)

# # 非主键查询
# stmt = select(Book).where(Book.name == book_name)

# =======================================================
# 什么时候用 session.get()：
# ✅ 通过主键查询单个对象
# ✅ 需要高性能（利用缓存）
# ✅ 代码简洁性优先

# 什么时候用 select()：
# ✅ 非主键字段查询
# ✅ 复杂查询条件（where、join、order by等）
# ✅ 需要返回多个结果
# ✅ 确保获取最新数据（绕过缓存）

# 最佳实践：
# - 主键单查询 → session.get(Model, pk)
# - 非主键单查询 → session.scalar(select(Model).where(...))
# - 非主键多查询 → session.scalars(select(Model).where(...)).all()