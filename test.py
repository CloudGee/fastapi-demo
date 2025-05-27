import asyncio
from contextlib import asynccontextmanager

@asynccontextmanager
async def my_async_context():
    print("异步进入")
    await asyncio.sleep(0.5)
    yield
    await asyncio.sleep(0.5)
    print("异步退出")

async def main():
    async with my_async_context():
        print("异步处理中")

asyncio.run(main())

# 异步进入
# 异步处理中
# 异步退出