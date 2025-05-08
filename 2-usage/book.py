from fastapi import FastAPI
from fastapi import HTTPException

from fakedb import loadBook

app = FastAPI()

books = loadBook()

@app.get("/")
def loadAllBooks():
    """
    获取所有书籍
    """
    return books

    