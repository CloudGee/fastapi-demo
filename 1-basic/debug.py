from fastapi import FastAPI, Path, HTTPException
import uvicorn

# 创建FastAPI实例
app = FastAPI()

# 示例数据
items = [
    {"id": 1, "name": "apple", "price": 3.5},
    {"id": 2, "name": "banana", "price": 2.0},
    {"id": 3, "name": "orange", "price": 4.2},
]

# 用于调试的简单函数
@app.get("/items/{item_id}")
def get_item(item_id: int = Path(..., description="商品ID", gt=0)):
    """
    用于演示断点调试的函数
    """
    # 在这里设置断点
    print(f"调试: 正在查找商品ID={item_id}")  # 调试输出

    # 查找商品
    for item in items:
        if item["id"] == item_id:
            # 在这里设置断点
            return item

    # 在这里设置断点
    raise HTTPException(status_code=404, detail=f"商品ID={item_id}不存在")

# 仅在直接运行此文件时启动服务器
if __name__ == "__main__":
    # 使用debug=True启动uvicorn，便于调试
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)