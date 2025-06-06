from fastapi import HTTPException, Depends, APIRouter
from sqlmodel import Session, select
from schema import Book, BookInput, Author, User
from db import get_db_session, db_exception_handler
from logging import Logger
from routers.auth import get_current_user

logger = Logger(__name__)


router = APIRouter(prefix="/api/book", tags=["Book"])

# 增
@router.post("/")
@db_exception_handler
def append_book(book_input: BookInput, session: Session = Depends(get_db_session)) -> Book:
    """
    添加书籍
    """
    # 检查书籍是否已存在
    existing_book_stmt = select(Book).where(Book.name == book_input.name)
    existing_book = session.exec(existing_book_stmt).first() # 注意：这里的first()方法会返回第一个匹配的结果，如果没有匹配的结果则返回None


    if existing_book:
        raise HTTPException(status_code=400, detail="Book already exists")

    # 查找或创建作者
    author_stmt = select(Author).where(Author.name == book_input.author, Author.nationality == book_input.author_nationality)
    existing_author = session.exec(author_stmt).first()

    if existing_author:
        target_author = existing_author
        logger.info(f"Found existing author: {existing_author.name}")
    else:
        # 创建新作者
        author_data = {"name": book_input.author}
        if book_input.author_nationality:
            author_data["nationality"] = book_input.author_nationality

        target_author = Author(**author_data)
        session.add(target_author)
        session.flush()  # 获取ID但不提交事务
        logger.info(f"Created new author: {target_author.name} with ID {target_author.id_}")

    # 创建新书籍
    book_data = book_input.model_dump(exclude={"author", "author_nationality"})
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
# ============ Step 4: Protected Route Endpoint ============
def get_books(
    # Query parameters (optional)
    type_: str | None = None,
    id_: int | None = None,

    # Dependency 3: Database session for book queries
    session: Session = Depends(get_db_session),

    # Dependency 4: Current user - THIS TRIGGERS THE ENTIRE AUTH FLOW
    # The 'user' variable will receive the return value from get_current_user, if authentication fails, it will raise an HTTPException
    user: User = Depends(get_current_user)
) -> list[Book]:
    """
    Authentication execution order:
    1. Request arrives -> FastAPI analyzes dependency tree
    2. Execute get_db_session() -> Creates database connection
    3. Execute security() -> Parses Authorization header into credentials
    4. Execute get_current_user() -> Validates user identity
    5. If authentication succeeds -> Execute route function with injected user
    6. If authentication fails -> Return 401, route function never executes

    The 'user' parameter contains the authenticated user object returned by get_current_user
    """

    # Only authenticated users can reach this point
    # The 'user' variable contains the authenticated user information
    # You can use it for:
    # - Logging user actions
    # - Role-based access control
    # - User-specific data filtering

    query = select(Book)
    if type_:
        query = query.where(Book.type_ == type_)
    if id_:
        query = query.where(Book.id_ == id_)

    # Could add user-based filtering here if needed:
    # if user.role != 'admin':
    #     query = query.where(Book.public == True)

    return session.exec(query).all()

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
def update_book(book_id: int, new_book: BookInput, session: Session = Depends(get_db_session)) -> Book:
    """
    更新书籍
    """
    try:
        # 查找现有作者
        author_stmt = select(Author).where(
            Author.name == new_book.author,
            Author.nationality == new_book.author_nationality
        )
        existing_author = session.exec(author_stmt).first()

        if existing_author:
            target_author = existing_author
        else:
            # 创建新作者 - 修复属性名
            author_data = {
                "name": new_book.author,
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
        new_book_data = new_book.model_dump(exclude={"author", "author_nationality"})
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