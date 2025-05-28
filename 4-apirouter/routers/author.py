from fastapi import HTTPException, Depends, APIRouter
from sqlmodel import Session, select
from schema import AuthorInput, Author
from db import get_db_session

router = APIRouter(prefix="/api/author", tags=["Author"])
# router 是一个APIRouter实例，用于组织和管理API路由，prefix="/api/author"表示所有路由都以/api/author开头，tags=["Author"]用于在API文档中分组。

# 有了prefix可以省略掉前缀/api/author，直接使用router的路由方法定义API接口。
@router.get("/")
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
def get_author_by_id(author_id: int, session: Session = Depends(get_db_session)) -> Author:
    """
    根据ID获取作者
    """
    author = session.get(Author, author_id)
    if author is None:
        raise HTTPException(status_code=404, detail=f"Author with id {author_id} not found")
    return author

@router.delete("/{author_id}")
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
