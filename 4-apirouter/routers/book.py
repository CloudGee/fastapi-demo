from fastapi import HTTPException, Depends, APIRouter
from sqlmodel import Session, select
from schema import BookInput, Book
from db import get_db_session


router = APIRouter(prefix="/api/book", tags=["Book"])

# 增
@router.post("/")
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


@router.get("/")
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
@router.get("/{book_id}")
def get_book_by_id(book_id: int, session: Session = Depends(get_db_session)) -> Book:
    """
    根据ID获取书籍
    """
    book = session.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
    return book


@router.delete("/{book_id}")
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



@router.put("/{book_id}")
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
    session.commit()  # 提交事务
    return book