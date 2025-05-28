from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import create_engine, SQLModel, Session, select
from schema import BookInput, Book, AuthorInput, Author
import uvicorn

engine = create_engine("sqlite:///books.db", echo=True, connect_args={"check_same_thread": False}) # SQLite数据库引擎，echo=True表示打印SQL语句，建议只在测试环境使用这个参数，connect_args={"check_same_thread": False}表示允许多线程访问

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

def get_db_session() -> Session:
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

# 增
@app.post("/api/book")
def append_book(book: BookInput, session: Session = Depends(get_db_session)) -> Book:
    """
    添加书籍
    """
    # Session 在数据库中一般称之为事务（Transaction），
    # 事务是一个操作的集合，这些操作要么全部成功，要么全部失败。如果有一个失败，之前的操作都会自动回滚。
    # 在这里，我们使用 Session 来管理数据库连接和操作。
    new_book = Book.model_validate(book)  # 将输入的BookInput转换为Book对象
    session.add(new_book)
    session.commit()  # 提交事务
    session.refresh(new_book) # 刷新new_book对象，获取最新的ID等信息
    return new_book


@app.get("/api/book")
def get_books(book_id: int | None = None, book_type: str | None = None, session: Session = Depends(get_db_session)) -> list[Book]:
    """
    获取书籍 - 支持条件查询和获取全部
    """
    filters = []
    if book_id is not None:
        filters.append(Book.id_ == book_id)  # 注意：去掉下划线
    if book_type is not None:
        filters.append(Book.type_ == book_type)  # 注意：去掉下划线

    query = select(Book)
    if filters:
        query = query.where(*filters)

    result = session.exec(query).all()
    if not result:
        raise HTTPException(status_code=404, detail="No books found")
    return result


# 查，通过主键查询，使用session.get()方法更加高效
@app.get("/api/book/{book_id}")
def get_book_by_id(book_id: int, session: Session = Depends(get_db_session)) -> Book:
    """
    根据ID获取书籍
    """
    book = session.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
    return book


@app.delete("/api/book/{book_id}")
def delete_book(book_id: int, session: Session = Depends(get_db_session)) -> str:
    """
    删除书籍
    """
    book = session.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
    session.delete(book)
    session.commit()
    return f"Book with id {book_id} deleted successfully"



@app.put("/api/book/{book_id}")
def update_book(book_id: int, new_book: BookInput, session: Session = Depends(get_db_session)) -> Book:
    """
    更新书籍
    """
    book = session.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
    book.name = new_book.name
    book.isbn = new_book.isbn
    book.type_ = new_book.type_
    book.publish = new_book.publish
    book.price = new_book.price
    return book

@app.get("/api/author")
def get_all_authors(session: Session = Depends(get_db_session)) -> list[Author]:
    """
    获取所有作者
    """
    query = select(Author)
    result = session.exec(query).all()
    if not result:
        raise HTTPException(status_code=404, detail="No authors found")
    return result

@app.post("/api/author")
def append_author(author: AuthorInput, session: Session = Depends(get_db_session)) -> Author:
    """
    添加作者
    """
    new_author = Author.model_validate(author)
    session.add(new_author)
    session.commit()
    session.refresh(new_author)
    return new_author

@app.get("/api/author/{author_id}")
def get_author_by_id(author_id: int, session: Session = Depends(get_db_session)) -> Author:
    """
    根据ID获取作者
    """
    author = session.get(Author, author_id)
    if author is None:
        raise HTTPException(status_code=404, detail=f"Author with id {author_id} not found")
    return author

@app.delete("/api/author/{author_id}")
def delete_author(author_id: int, session: Session = Depends(get_db_session)) -> str:
    """
    删除作者
    """
    author = session.get(Author, author_id)
    if author is None:
        raise HTTPException(status_code=404, detail=f"Author with id {author_id} not found")
    session.delete(author)
    session.commit()
    return f"Author with id {author_id} deleted successfully"

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