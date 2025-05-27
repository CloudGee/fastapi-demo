# pydantic包是一个数据验证和设置管理的库，使用Python类型提示来定义数据模型
# 它可以自动验证数据的类型和格式，并提供友好的错误消息
# 它也可以将数据自动转换为指定的类型
# 还可以将数据模型序列化为JSON格式
# 还可以将JSON格式的数据反序列化为Python对象
# 还可以将数据模型转换为字典格式
# 还可以将字典格式的数据转换为数据模型

from pydantic import BaseModel

class BookInput(BaseModel):
    name: str
    isbn: str
    type_: str
    publish: str
    price: float

    # 为api doc中每个api接口添加有意义的示例描述
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

class BookOutput(BookInput):
    id_: int

    # 为api doc中每个api接口添加有意义的示例描述
    class Config:
        json_schema_extra = {
            "example": {
                "id_": 1,
                "name": "Python",
                "isbn": "978-7-121-30000-0",
                "type_": "programming",
                "publish": "2023-01-01",
                "price": 99.99
            }
        }


if __name__ == "__main__":
    book = Book(
        _id=1, # private key, _在变量名前面代表私有变量。pydantic会忽略这个字段，因此最好把_id替换为id_
        id_=1,
        name="Python",
        isbn="978-7-121-30000-0",
        type_="programming", # correct way
        publish="2023-01-01",
        price=99.99
    )
    print(book)
    print(book.name)

    book2 = Book(
        id_=2,
        name="Java",
        isbn="978-7-121-30000-0",
        type_="programming",
        publish="2023-01-01",
        price="99.99"
    )
    print(book2)

    print(type(book.model_dump()))
    print(type(book.model_dump_json()))