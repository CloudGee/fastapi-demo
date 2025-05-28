

from sqlmodel import Field, SQLModel, Relationship


class BookBase(SQLModel):
    name: str
    isbn: str
    type_: str
    publish: str
    price: float


    class Config:
        json_schema_extra = {
            "example": {
                "name": "Python",
                "isbn": "978-7-121-30000-0",
                "type_": "programming",
                "publish": "2023-01-01",
                "price": 99.99
            }
        }

class BookInput(BookBase):
    author: str
    author_nationality: str | None = None  # 可选字段
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Python",
                "isbn": "978-7-121-30000-0",
                "type_": "programming",
                "publish": "2023-01-01",
                "price": 99.99,
                "author": "Guido van Rossum",
                "author_nationality": "Dutch"
            }
        }

class Book(BookBase, table=True):
    id_: int | None = Field(default=None, primary_key=True)
    author_id: int = Field(foreign_key="author.id_")
    author: "Author" = Relationship(back_populates="books")

    class Config:
        json_schema_extra = {
            "example": {
                "id_": 1,
                "name": "Python",
                "isbn": "978-7-121-30000-0",
                "type_": "programming",
                "publish": "2023-01-01",
                "price": 99.99,
                "author_id": 1  # 外键，指向作者表的id
            }
        }

class AuthorInput(SQLModel):
    name: str
    nationality: str | None = None  # 可选字段
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Guido van Rossum",
                "nationality": "Dutch"
            }
        }

class Author(AuthorInput, table=True):
    id_: int | None = Field(default=None, primary_key=True)

    books: list[Book] = Relationship(back_populates="author")
    class Config:
        json_schema_extra = {
            "example": {
                "id_": 1,
                "name": "Guido van Rossum",
                "nationality": "Dutch"
            }
        }

class AuthorOutputWithBooks(AuthorInput):
    books: list[Book] = []
    class Config:
        json_schema_extra = {
            "example": {
                "id_": 1,
                "name": "Guido van Rossum",
                "books": [
                    {
                        "id_": 1,
                        "name": "Python",
                        "isbn": "978-7-121-30000-0",
                        "type_": "programming",
                        "publish": "2023-01-01",
                        "price": 99.99
                    }
                ]
            }
        }