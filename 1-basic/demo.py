from fastapi import FastAPI, Query, Path, HTTPException
from typing import Optional

# 创建 FastAPI 实例
app = FastAPI()

# 伪造数据，直接使用字典列表
items = [
    {"id": 1, "name": "apple", "price": 3.5},
    {"id": 1, "name": "apple", "price": 4},
    {"id": 2, "name": "banana", "price": 2.0},
    {"id": 3, "name": "orange", "price": 4.2},
]

# 方法：@app.get 装饰器定义路由，Query参数处理查询参数
# 知识点：Optional类型提示，返回类型注解，Query参数校验
# 参数类型：name - 类型参数(Typed Parameter)，使用Query修饰
@app.get("/items/")
def get_items(
    name: Optional[str] = Query(None, description="按名称过滤（可选）")
) -> list[dict]:
    """
    name 是查询参数（?name=xxx），类型为 Optional[str]。
    FastAPI 会自动从 URL 中解析并进行类型转换，转换为函数定义中指定的类型。
    返回类型 list[dict]，FastAPI 自动校验是否符合。Python语言本身默认不会校验返回值。
    """
    if name:
        return [item for item in items if item["name"] == name]
    return items

# 方法：路径参数{item_id}，Path校验路径参数
# 知识点：Path必填参数(...表示必填)，返回类型注解，HTTPException异常处理
# 参数类型：item_id - 路径参数(Path Parameter)，使用Path修饰
@app.get("/items/{item_id}")
def get_item_by_id(
    item_id: int = Path(..., description="按 ID 查询商品", gt=0)
) -> dict:
    """
    item_id 是路径参数，类型为 int, 会自动转换浏览器的输入为函数指定类型。
    FastAPI 会校验类型，并进行自动类型转换，使用方式不匹配时返回 422。
    返回 dict 类型，返回类型不符将抛出自定义异常。

    Path函数说明：
    - Path用于声明和校验URL路径参数
    - ... 表示参数必填（不可能有默认值，因为路径参数必须存在）
    - gt=0 表示数值需要大于0（gt: greater than）
    - 支持的验证参数包括：gt, ge, lt, le, regex等
    """
    for item in items:
        if item["id"] == item_id:
            if isinstance(item, dict):
                return item
            else:
                raise HTTPException(status_code=404, detail="Item not found")
    raise HTTPException(status_code=404, detail="Item not found")

# 方法：Query处理多个查询参数，设置默认值
# 知识点：多参数处理，返回值类型校验，参数默认值设置
# 参数类型：price, tax - 类型参数(Typed Parameter)，使用Query修饰
@app.get("/calc")
def calc_price(
    price: float = Query(..., description="基础价格"),
    tax: float = Query(0.1, description="税率，默认0.1")
) -> float:
    """
    price 和 tax 是查询参数，类型为 float。
    返回类型是 float, 若返回不符合则抛出异常。
    """
    return round(price * (1 + tax), 2)

# 方法：多路径参数处理，HTTPException自定义错误
# 知识点：多路径参数解析，类型校验，错误处理
# 参数类型：a, b - 路径参数(Path Parameter)，使用Path修饰
@app.get("/divide/{a}/{b}")
def divide(
    a: int = Path(..., description="被除数"),
    b: int = Path(..., description="除数", ne=0)
) -> float:
    """
    使用路径参数 + 类型注解, FastAPI 校验输入类型。
    返回 float, 若 b 为 0 抛出 HTTP 400 异常。

    Path函数说明：
    - ne=0 参数表示不等于0（ne: not equal）
    - 这样FastAPI会自动验证并在b=0时返回422错误
    - 但这里仍保留了自定义异常，展示错误处理方式
    """
    if b == 0:
        raise HTTPException(status_code=400, detail="除数不能为0")
    return a / b

# 方法：组合查询参数，逐步过滤
# 知识点：多条件过滤，链式过滤，Optional参数处理
# 参数类型：name, price - 类型参数(Typed Parameter)，使用Query修饰
@app.get("/items/search")
def search_items(
    name: Optional[str] = Query(None, description="按名称搜索"),
    price: Optional[float] = Query(None, description="按价格搜索")
) -> list[dict]:
    """
    联合查询示例：
    - name 和 price 是查询参数，可以单独使用，也可以同时使用。
    - FastAPI 会根据类型自动转换和校验。
    - 返回匹配的项组成的 list。
    """
    results = items
    if name is not None:
        results = [item for item in results if item["name"] == name]
    if price is not None:
        results = [item for item in results if item["price"] == price]
    return results

# 方法：使用Python 3.10+ 联合类型语法(|)代替Optional
# 知识点：新型联合类型语法，None默认值处理，skip_validating设置
# 参数类型：min_price, max_price, category - 类型参数(Typed Parameter)，使用Query修饰
# 参数类型：skip_validating - 普通参数(Normal Parameter)，有默认值
@app.get("/items/filter")
def filter_items(
    min_price: float | None = Query(None, description="最低价格过滤", ge=0),
    max_price: int | None = Query(None, description="最高价格过滤"),
    category: str | None = Query(None, description="商品类别"),
    skip_validating: bool = Query(False, description="是否跳过验证")
) -> list[dict]:
    """
    使用Python 3.10+ 联合类型语法示例：
    - min_price, max_price, category 是类型参数(Typed Parameter)，使用Query修饰
    - skip_validating 是类型参数(Typed Parameter)，有默认值False
    - min_price 使用 float|None 替代 Optional[float]
    - max_price 使用 int|None 替代 Optional[int]
    - category 使用 str|None 替代 Optional[str]
    - 支持多条件组合过滤
    """
    results = items

    if min_price is not None:
        results = [item for item in results if item["price"] >= min_price]

    if max_price is not None:
        results = [item for item in results if item["price"] <= max_price]

    # 假设items中有category字段
    if category is not None:
        results = [item for item in results if item.get("category") == category]

    # 演示bool类型参数的使用
    if skip_validating:
        return results

    # 假设有验证逻辑
    return [item for item in results if "validated" in item or not skip_validating]

# 添加一个展示Path高级验证的路由
# 参数类型：item_id - 路径参数(Path Parameter)，使用Path高级验证
@app.get("/items/validate/{item_id}")
def validate_item_id(
    item_id: int = Path(
        ...,
        description="商品ID",
        gt=0,               # 大于0
        le=1000,            # 小于等于1000
        title="商品标识符",   # 在文档中显示的标题
    )
) -> dict:
    """
    Path函数详细使用示例：

    Path函数用于声明和验证路径参数，可以提供以下功能：
    1. 参数验证：
       - gt (greater than): 大于某值
       - ge (greater than or equal): 大于等于某值
       - lt (less than): 小于某值
       - le (less than or equal): 小于等于某值
       - ne (not equal): 不等于某值

    2. 字符串验证（用于字符串类型参数）：
       - min_length: 最小长度
       - max_length: 最大长度
       - regex: 正则表达式匹配

    3. 文档说明：
       - description: 参数描述
       - title: 参数标题
       - deprecated: 标记参数为已弃用
       - example: 提供示例值

    与Query的区别：
    - Path用于路径参数（URL路径的一部分）
    - Query用于查询参数（URL中?后的部分）
    - Path参数总是必填的，因此...是必需的
    - Path参数验证失败会返回422状态码
    """
    return {"item_id": item_id, "validated": True}

# 添加一个同时包含三种参数类型的路由
# 参数类型：product_id - 路径参数(Path Parameter)
# 参数类型：user_id - 类型参数(Typed Parameter)，使用Query修饰
# 参数类型：include_details - 普通参数(Normal Parameter)，有默认值
@app.get("/products/{product_id}")
def get_product(
    product_id: int = Path(..., description="产品ID", gt=0),
    user_id: str | None = Query(None, description="用户ID"),
    include_details: bool = False
) -> dict:
    """
    复合参数类型示例：
    - product_id 是路径参数(Path Parameter)，必填
    - user_id 是类型参数(Typed Parameter)，通过Query修饰，可选
    - include_details 是普通参数(Normal Parameter)，有默认值False

    FastAPI参数类型说明：
    1. 路径参数(Path Parameter): 出现在URL路径中的参数，用{}标记，通常用Path()修饰
    2. 类型参数(Typed Parameter): 使用Query、Body等修饰的参数，带有额外验证规则
    3. 普通参数(Normal Parameter): 没有特殊修饰的参数，通常有默认值
    """
    # 模拟业务逻辑
    product = {"id": product_id, "name": f"Product {product_id}", "price": product_id * 10}

    if user_id:
        product["user_specific"] = f"Custom data for user {user_id}"

    if include_details:
        product["details"] = {
            "description": f"Detailed info for product {product_id}",
            "specs": ["Spec1", "Spec2", "Spec3"],
            "reviews": ["Good", "Excellent", "Average"]
        }

    return product

# ------------ 运行说明 ------------
"""
1. 基本运行命令（默认端口8000）：
   uvicorn pyFileName:app --reload

2. 指定端口运行（例如9000端口）：
   uvicorn pyFileName:app --reload --port 9000

3. 指定主机IP（允许外部访问）：
   uvicorn pyFileName:app --reload --host 0.0.0.0 --port 8000

4. 生产环境运行（关闭重载）：
   uvicorn pyFileName:app --workers 4

5. 参数说明：
   - pyFileName:app：pyFileName是Python文件名，app是FastAPI实例变量名
   - --reload：开发模式，代码修改自动重载
   - --port：指定运行端口，默认8000
   - --host：指定监听主机，默认127.0.0.1（仅本地访问）
   - --workers：工作进程数，生产环境使用，默认1

6. 文档地址（启动后自动生成）：
   - Swagger UI(交互式文档)：http://127.0.0.1:8000/docs
   - ReDoc(美观文档)：http://127.0.0.1:8000/redoc
   - OpenAPI JSON规范：http://127.0.0.1:8000/openapi.json
"""