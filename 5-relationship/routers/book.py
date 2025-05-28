from fastapi import HTTPException, Depends, APIRouter, logger
from sqlmodel import Session, select
from schema import Book, BookWithAuthors, Author
from db import get_db_session, db_exception_handler


router = APIRouter(prefix="/api/book", tags=["Book"])

# 增
@router.post("/")
@db_exception_handler
def append_book(book_input: BookWithAuthors, session: Session = Depends(get_db_session)) -> Book:
    """
    添加书籍
    """
    # 检查书籍是否已存在
    existing_book_stmt = select(Book).where(Book.name == book_input.name)
    existing_book = session.exec(existing_book_stmt).scalar_one_or_none() # 期望返回单个结果或None，如果有多个结果会抛出异常

    if existing_book:
        raise HTTPException(status_code=400, detail="Book already exists")

    # 查找或创建作者
    author_stmt = select(Author).where(Author.name == book_input.author_name, Author.nationality == book_input.author_nationality)
    existing_author = session.exec(author_stmt).scalar_one_or_none()

    if existing_author:
        target_author = existing_author
        logger.info(f"Found existing author: {existing_author.name}")
    else:
        # 创建新作者
        author_data = {"name": book_input.author_name}
        if book_input.author_nationality:
            author_data["nationality"] = book_input.author_nationality

        target_author = Author(**author_data)
        session.add(target_author)
        session.flush()  # 获取ID但不提交事务
        logger.info(f"Created new author: {target_author.name} with ID {target_author.id_}")

    # 创建新书籍
    book_data = book_input.model_dump(exclude={"author_name", "author_nationality"})
    book_data["author_id"] = target_author.id_

    new_book = Book(**book_data)
    session.add(new_book)

    # 统一提交事务
    session.commit()
    session.refresh(new_book)

    logger.info(f"Successfully created book: {new_book.name}")
    return new_book

@router.get("/")
@db_exception_handler
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
@db_exception_handler
def get_book_by_id(book_id: int, session: Session = Depends(get_db_session)) -> Book:
    """
    根据ID获取书籍
    """
    book = session.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
    return book


@router.delete("/{book_id}")
@db_exception_handler
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
def update_book(book_id: int, new_book: BookWithAuthors, session: Session = Depends(get_db_session)) -> Book:
    """
    更新书籍
    """
    try:
        # 查找现有作者
        author_stmt = select(Author).where(
            Author.name == new_book.author_name,
            Author.nationality == new_book.author_nationality
        )
        existing_author = session.exec(author_stmt).scalar_one_or_none()

        if existing_author:
            target_author = existing_author
        else:
            # 创建新作者 - 修复属性名
            author_data = {
                "name": new_book.author_name,
                "nationality": new_book.author_nationality  # 修复：使用正确的属性名
            }
            target_author = Author(**author_data)
            session.add(target_author)
            session.flush()  # 确保获得ID
            session.refresh(target_author)  # 添加：刷新对象确保所有属性可用
            logger.info(f"Created new author: {target_author.name} with ID {target_author.id_}")

        # 查找要更新的书籍
        book = session.get(Book, book_id)
        if book is None:
            raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")

        # 准备更新数据
        new_book_data = new_book.model_dump(exclude={"author_name", "author_nationality"})
        new_book_data["author_id"] = target_author.id_

        # 更新书籍属性
        for key, value in new_book_data.items():
            setattr(book, key, value)

        session.commit()
        session.refresh(book)  # 添加：刷新书籍对象
        return book

    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating book: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")