import json

def loadBook() -> list[dict]:
    with open('books.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data