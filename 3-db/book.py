from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import create_engine, SQLModel, Session, select
from schema import BookInput, BookOutput, Book


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

@app.post("/append")
def append_book(book: BookInput, session: Session = Depends(get_db_session)) -> Book:
    """
    添加书籍
    """
    # Session 在数据库中一般称之为事务（Transaction），
    # 事务是一个操作的集合，这些操作要么全部成功，要么全部失败。如果有一个失败，之前的操作都会自动回滚。
    # 在这里，我们使用 Session 来管理数据库连接和操作。
    new_book = Book.model_validate(BookInput)  # 将输入的BookInput转换为Book对象
    session.add(new_book)
    session.commit()  # 提交事务
    session.refresh(new_book) # 刷新new_book对象，获取最新的ID等信息
    return new_book

@app.get("/")
def load_all_books(session: Session = Depends(get_db_session)) -> list[Book]:
    """
    获取所有书籍
    """
    query = select(Book)
    result = session.exec(query).all()
    if not result:
        raise HTTPException(status_code=404, detail="No books found")
    return result

@app.get("/search")
def get_book(book_id: int | None = None, book_type: str | None = None, session: Session = Depends(get_db_session)) -> list[Book]:
    filters = []
    if book_id is not None:
        filters.append(Book.id_ == book_id)
    if book_type is not None:
        filters.append(Book.type_ == book_type)

    query = select(Book).where(*filters)
    result = session.exec(query).all() # 执行查询并返回所有结果，结果是一个list
    if not result:
        raise HTTPException(status_code=404, detail="No books found matching the criteria")
    return result



@app.get("/search/{book_id}")
def get_book_by_id(book_id: int, session: Session = Depends(get_db_session)) -> Book:
    """
    根据ID获取书籍
    """
    book = session.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
    return book


@app.delete("/delete/{book_id}")
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



@app.put("/update/{book_id}")
def update_book(book_id: int, book: BookInput, session: Session = Depends(get_book_by_id)) -> Book:
    """
    更新书籍
    """
