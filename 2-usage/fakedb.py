import json
from schema import BookOutput, BookInput

def loadBook() -> list:
    with open('book.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        return [BookOutput(**book) for book in data]

def saveBook(books: list[BookInput]) -> None:
    with open('book.json', 'w', encoding='utf-8') as f:
        json.dump([book.model_dump() for book in books], f, ensure_ascii=False, indent=4)
    return None

