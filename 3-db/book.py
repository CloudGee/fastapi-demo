from fastapi import FastAPI
from fastapi import HTTPException

from sqlmodel import create_engine, SQLModel
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

@app.get("/")
def load_all_books() -> list[BookOutput]:
    """
    获取所有书籍
    """
    print(books)
    return books

@app.get("/search")
def get_book(book_id: int|None = None, book_type: str|None = None) -> list[BookOutput]:
    allBook = books
    if book_id is not None:
        allBook = [book for book in allBook if book.id_ == book_id]
    if book_type is not None:
        allBook = [book for book in allBook if book.type_ == book_type]
    return allBook

@app.get("/search/{book_id}")
def get_book_by_id(book_id: int) -> BookOutput:
    """
    根据ID获取书籍
    """
    for book in books:
        if book.id_ == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")



@app.post("/append")
def append_book(book: BookInput) -> BookOutput:
    """
    添加书籍
    """
    bookWithID = BookOutput(
        id_=len(books) + 1,
        name=book.name,
        isbn=book.isbn,
        type_=book.type_,
        publish=book.publish,
        price=book.price
    )
    books.append(bookWithID)
    try:
        saveBook(books)
        return bookWithID
    except Exception as e:
        print(f"Error saving book: {e}")
        raise HTTPException(status_code=500, detail="Error saving book")

@app.delete("/delete/{book_id}")
def delete_book(book_id: int):
    """
    删除书籍
    """
    for book in books:
        if book.id_ == book_id:
            books.remove(book)
            try:
                saveBook(books)
                return {"message": "Book deleted successfully"}
            except Exception as e:
                print(f"Error delete book: {e}")
                raise HTTPException(status_code=500, detail="Error deleting book")
    raise HTTPException(status_code=404, detail="Book not found")

@app.put("/update/{book_id}")
def update_book(book_id: int, book: BookInput) -> BookOutput:
    """
    更新书籍
    """
    for i, b in enumerate(books):
        if b.id_ == book_id:
            books[i] = BookOutput(
                id_=book_id,
                name=book.name,
                isbn=book.isbn,
                type_=book.type_,
                publish=book.publish,
                price=book.price
            )
            try:
                saveBook(books)
                return books[i]
            except Exception as e:
                print(f"Error updating book: {e}")
                raise HTTPException(status_code=500, detail="Error updating book")
    raise HTTPException(status_code=404, detail="Book not found")