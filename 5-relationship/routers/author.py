from fastapi import HTTPException, Depends, APIRouter
from sqlmodel import Session, select
from schema import AuthorInput, Author, AuthorOutputWithBooks, BookBase, Book
from db import get_db_session, db_exception_handler

router = APIRouter(prefix="/api/author", tags=["Author"])
# router 是一个APIRouter实例，用于组织和管理API路由，prefix="/api/author"表示所有路由都以/api/author开头，tags=["Author"]用于在API文档中分组。

# 有了prefix可以省略掉前缀/api/author，直接使用router的路由方法定义API接口。
@router.get("/")
@db_exception_handler
def get_all_authors(session: Session = Depends(get_db_session)) -> list[Author]:
    """
    获取所有作者
    """
    query = select(Author)
    result = session.exec(query).all()
    if not result:
        raise HTTPException(status_code=404, detail="No authors found")
    return result

@router.post("/")
@db_exception_handler
def append_author(author: AuthorInput, session: Session = Depends(get_db_session)) -> Author:
    """
    添加作者
    """
    new_author = Author.model_validate(author)
    session.add(new_author)
    session.commit()
    session.refresh(new_author)
    return new_author

@router.get("/{author_id}")
@db_exception_handler
def get_author_by_id(author_id: int, session: Session = Depends(get_db_session)) -> Author:
    """
    根据ID获取作者
    """
    author = session.get(Author, author_id)
    if author is None:
        raise HTTPException(status_code=404, detail=f"Author with id {author_id} not found")
    return author

@router.delete("/{author_id}")
@db_exception_handler
def delete_author(author_id: int, session: Session = Depends(get_db_session)) -> dict:
    """
    删除作者（改进版）
    """
    author = session.get(Author, author_id)
    if author is None:
        raise HTTPException(status_code=404, detail=f"Author with id {author_id} not found")

    # 检查是否有关联的书籍
    books_count = session.exec(select(Book).where(Book.author_id == author_id)).first()
    if books_count:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete author with id {author_id}: author has associated books"
        )

    try:
        session.delete(author)
        session.commit()
        return {"message": f"Author with id {author_id} deleted successfully"}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete author: {str(e)}")

@router.get("/{author_id}/books")
@db_exception_handler
def get_books_by_author(author_id: int, session: Session = Depends(get_db_session)) -> AuthorOutputWithBooks:
    """
    根据作者ID获取该作者的所有书籍
    """
    author = session.get(Author, author_id)
    if author is None:
        raise HTTPException(status_code=404, detail=f"Author with id {author_id} not found")
    # return 的时候会把Author类型转换为AuthorOutputWithBooks类型，而AuthorOutputWithBooks中有定义books，会触发SQLModel的关系加载，自动加载查询该作者的所有书籍
    return author

@router.post("/{author_id}/books")
@db_exception_handler
def append_bood_by_author_id(author_id: int, book: BookBase, session: Session = Depends(get_db_session)) -> Book:
    """
    为指定作者添加书籍
    """
    author = session.get(Author, author_id)
    if author is None:
        raise HTTPException(status_code=404, detail=f"Author with id {author_id} not found")

    new_book = Book.model_validate(book, update={"author_id": author_id})
    session.add(new_book)
    session.commit()
    session.refresh(new_book)
    return new_book