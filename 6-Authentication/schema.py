

from sqlmodel import Field, SQLModel, Relationship
# pip install "passlib[bcrypt]"
# pass lib bcrypt is used to hash the password
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
    author: "Author" = Relationship(back_populates="books")
    author_id: int = Field(foreign_key="author.id_")

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
#
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

# user class
# it should be an sqlmodel class
# it should have a username, password_hash and id as primary key
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    # index true means that the username will be indexed for faster search
    # index is a performance optimization for searching in the database
    username: str = Field(index=True, unique=True)
    # optional: username: str = Field(sa_column=Column('username', VARCHAR, unique=True, index=True)), different way to define the same thing
    password_hash: str
    def set_password(self, password: str):
        """Set the password hash using bcrypt."""
        self.password_hash = pwd_context.hash(password)
    def verify_password(self, password: str) -> bool:
        """Verify the password against the stored hash."""
        return pwd_context.verify(password, self.password_hash)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "john_doe",
                "password_hash": "hashed_password"
            }
        }

class UserOutput(SQLModel):
    id: int
    username: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "john_doe"
            }
        }
