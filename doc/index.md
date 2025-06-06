# FastAPI 完整学习笔记：从基础到高级实践

## 1. FastAPI 基础知识与环境配置

### 1.1 FastAPI 简介与优势

FastAPI 是一个现代、高性能的 Python Web 框架，专为构建 API 而设计。它基于 Python 3.6+ 的类型提示，提供了以下核心优势：

- **高性能**：与 NodeJS 和 Go 相当的性能表现
- **快速开发**：减少约 40% 的代码编写时间
- **自动文档**：基于 OpenAPI 和 JSON Schema 自动生成交互式文档
- **类型安全**：完整的类型提示支持，提供编辑器智能提示
- **易于学习**：直观的设计，减少学习成本

### 1.2 安装与基础配置

```bash
# 创建虚拟环境（推荐）
python -m venv fastapi-env
source fastapi-env/bin/activate  # Linux/Mac
fastapi-env\Scripts\activate     # Windows

# 安装 FastAPI 及标准依赖
pip install "fastapi[standard]"

# 最小化安装
pip install fastapi uvicorn

# 启动开发服务器
fastapi dev main.py
```

### 1.3 开发容器配置

在 `.devcontainer/devcontainer.json` 中配置开发环境：

```json
{
    "name": "FastAPI Development",
    "image": "python:3.11-slim",
    "features": {
        "ghcr.io/devcontainers/features/python:1": {}
    },
    "forwardPorts": [8000],
    "postCreateCommand": "pip install fastapi[standard] uvicorn",
    "customizations": {
        "vscode": {
            "extensions": [
                "ms-python.python",
                "ms-python.pylance"
            ]
        }
    }
}
```

### 1.4 Docker 容器化配置

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]
```

Docker Compose 配置示例：

```yaml
version: '3.8'
services:
  fastapi:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - ENV=development
    command: fastapi dev main.py --host 0.0.0.0
```

## 2. 路由系统：路径参数与查询参数

### 2.1 基础路由结构

```python
from fastapi import FastAPI

app = FastAPI()

# 基本 GET 路由
@app.get("/")
async def root():
    return {"message": "Hello World"}

# 支持的 HTTP 方法
@app.get("/items")      # GET 请求
@app.post("/items")     # POST 请求
@app.put("/items/{id}") # PUT 请求
@app.delete("/items/{id}") # DELETE 请求
```

### 2.2 路径参数详解

```python
# 基本路径参数
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

# 多个路径参数
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(user_id: int, item_id: str):
    return {"user_id": user_id, "item_id": item_id}

# 枚举类型路径参数
from enum import Enum

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    return {"model_name": model_name}
```

### 2.3 查询参数与验证

```python
from fastapi import Query

# 基本查询参数
@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

# 带验证的查询参数
@app.get("/items/")
async def read_items(
    q: str = Query(None, min_length=3, max_length=50),
    page: int = Query(1, ge=1),  # 大于等于 1
    size: int = Query(10, le=100)  # 小于等于 100
):
    return {"q": q, "page": page, "size": size}

# 必需查询参数
@app.get("/items/")
async def read_items(q: str):  # 没有默认值 = 必需参数
    return {"q": q}
```

### 2.4 路由优先级

```python
# 路由顺序很重要 - 更具体的路由要放在前面
@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}

@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}
```

## 3. Pydantic 模型与数据验证

### 3.1 基础 Pydantic 模型

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)

# 使用模型
@app.post("/users/")
async def create_user(user: User):
    return user
```

### 3.2 高级验证与字段约束

```python
from pydantic import BaseModel, Field, validator

class Item(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=300)
    price: float = Field(..., gt=0, description="价格必须大于零")
    tax: Optional[float] = Field(None, ge=0, le=1)

# 自定义验证器
class User(BaseModel):
    name: str
    email: str
    password: str
    confirm_password: str

    @validator('email')
    def email_must_contain_at(cls, v):
        if '@' not in v:
            raise ValueError('邮箱格式无效')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('密码不匹配')
        return v
```

### 3.3 嵌套模型与响应模型

```python
class Address(BaseModel):
    street: str
    city: str
    country: str

class User(BaseModel):
    name: str
    email: str
    address: Address

# 响应模型过滤
class UserIn(BaseModel):
    name: str
    email: str
    password: str

class UserOut(BaseModel):
    name: str
    email: str

@app.post("/users/", response_model=UserOut)
async def create_user(user: UserIn):
    return user  # 密码会被自动过滤
```

## 4. SQLModel 数据库集成

### 4.1 SQLModel 基础配置

```python
from sqlmodel import SQLModel, Field, create_engine, Session, select
from fastapi import FastAPI, Depends
from typing import Annotated

# 模型定义
class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)
    secret_name: str

# 数据库设置
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
```

### 4.2 数据库会话管理

```python
def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

# 在路由中使用会话
@app.post("/heroes/")
def create_hero(hero: Hero, session: SessionDep) -> Hero:
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero
```

### 4.3 生产环境配置

```python
from sqlalchemy.pool import StaticPool

# 生产环境配置
engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False  # 开发环境设置为 True
)
```

## 5. CRUD 操作实现

### 5.1 多模型模式

```python
# 基础模型
class HeroBase(SQLModel):
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)

# 数据库表模型
class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    secret_name: str

# API 数据模型
class HeroCreate(HeroBase):
    secret_name: str

class HeroPublic(HeroBase):
    id: int

class HeroUpdate(HeroBase):
    name: str | None = None
    age: int | None = None
    secret_name: str | None = None
```

### 5.2 完整 CRUD 实现

```python
from fastapi import HTTPException

# 创建
@app.post("/heroes/", response_model=HeroPublic)
def create_hero(hero: HeroCreate, session: SessionDep):
    db_hero = Hero.model_validate(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero

# 读取（列表）
@app.get("/heroes/", response_model=list[HeroPublic])
def read_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: int = Query(default=100, le=100)
):
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes

# 读取（单个）
@app.get("/heroes/{hero_id}", response_model=HeroPublic)
def read_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="英雄未找到")
    return hero

# 更新
@app.patch("/heroes/{hero_id}", response_model=HeroPublic)
def update_hero(hero_id: int, hero: HeroUpdate, session: SessionDep):
    hero_db = session.get(Hero, hero_id)
    if not hero_db:
        raise HTTPException(status_code=404, detail="英雄未找到")
    hero_data = hero.model_dump(exclude_unset=True)
    hero_db.sqlmodel_update(hero_data)
    session.add(hero_db)
    session.commit()
    session.refresh(hero_db)
    return hero_db

# 删除
@app.delete("/heroes/{hero_id}")
def delete_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="英雄未找到")
    session.delete(hero)
    session.commit()
    return {"ok": True}
```

## 6. API 路由组织与项目结构

### 6.1 推荐的项目结构

```
fastapi-project/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用实例
│   ├── dependencies.py      # 公共依赖
│   ├── routers/            # 路由模块
│   │   ├── __init__.py
│   │   ├── users.py
│   │   ├── items.py
│   │   └── admin.py
│   ├── models/             # 数据库模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── item.py
│   ├── schemas/            # Pydantic 模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── item.py
│   ├── services/           # 业务逻辑
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   └── item_service.py
│   ├── core/              # 核心功能
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── security.py
│   └── tests/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

### 6.2 主应用文件结构

```python
# main.py
from fastapi import FastAPI
from app.routers import users, items
from app.core.config import settings

app = FastAPI(
    title="FastAPI 应用",
    description="综合性的 API",
    version="1.0.0"
)

# 包含路由
app.include_router(users.router, prefix="/api/v1")
app.include_router(items.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "欢迎使用 FastAPI"}
```

### 6.3 路由模块示例

```python
# routers/users.py
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import User, UserCreate
from app.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "未找到"}}
)

@router.get("/", response_model=list[User])
async def read_users(skip: int = 0, limit: int = 100):
    return UserService.get_users(skip=skip, limit=limit)

@router.post("/", response_model=User)
async def create_user(user: UserCreate):
    return UserService.create_user(user)
```

## 7. 数据库关系与外键

### 7.1 一对多关系

```python
from sqlmodel import Relationship

class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str
    heroes: list["Hero"] = Relationship(back_populates="team")

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    team_id: int | None = Field(default=None, foreign_key="team.id")
    team: Team | None = Relationship(back_populates="heroes")
```

### 7.2 多对多关系

```python
class HeroTeamLink(SQLModel, table=True):
    team_id: int | None = Field(default=None, foreign_key="team.id", primary_key=True)
    hero_id: int | None = Field(default=None, foreign_key="hero.id", primary_key=True)

class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str
    heroes: list["Hero"] = Relationship(back_populates="teams", link_model=HeroTeamLink)

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    teams: list[Team] = Relationship(back_populates="heroes", link_model=HeroTeamLink)
```

### 7.3 一对一关系

```python
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    profile: "UserProfile" = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"uselist": False}
    )

class UserProfile(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    bio: str
    user: User = Relationship(back_populates="profile")
```

## 8. HTTP 基本认证实现

### 8.1 基础认证设置

```python
import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

def get_current_username(
    credentials: HTTPBasicCredentials = Depends(security)
):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = b"admin"
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )

    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = b"secret"
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )

    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/protected")
def protected_route(username: str = Depends(get_current_username)):
    return {"message": f"你好 {username}!"}
```

### 8.2 运维考虑因素

- **安全性**：生产环境中必须使用 HTTPS
- **性能**：每次请求都会发送凭证
- **部署**：适合防火墙后的内部服务
- **监控**：记录认证尝试以进行安全审计

## 9. 密码哈希与安全最佳实践

### 9.1 bcrypt 密码哈希

```python
from passlib.context import CryptContext

# 创建密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# 用户认证示例
def authenticate_user(username: str, password: str):
    user = get_user_from_db(username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user
```

### 9.2 JWT 令牌认证

```python
from datetime import datetime, timedelta, timezone
import jwt
from fastapi.security import OAuth2PasswordBearer

# 配置
SECRET_KEY = "your-256-bit-secret-key"  # 使用环境变量
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user
```

### 9.3 安全最佳实践

```python
# 环境配置
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str
    database_url: str
    cors_origins: list[str] = []

    class Config:
        env_file = ".env"
        case_sensitive = False

# 安全头中间件
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# 输入验证
from pydantic import BaseModel, validator
import re

class UserInput(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')

    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('用户名只能包含字母数字和下划线')
        return v
```

## 10. 错误处理与异常管理

### 10.1 集中式异常处理

```python
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

# 自定义异常基类
class BaseAPIException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

# 全局异常处理器
@app.exception_handler(BaseAPIException)
async def api_exception_handler(request: Request, exc: BaseAPIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "request_id": getattr(request.state, 'request_id', None)}
    )

# 未处理异常日志记录
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "内部服务器错误"}
    )

# 验证错误处理
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "数据验证错误", "errors": exc.errors()}
    )
```

### 10.2 业务异常定义

```python
class UserNotFoundError(BaseAPIException):
    def __init__(self, user_id: int):
        super().__init__(status_code=404, detail=f"用户 {user_id} 未找到")

class InsufficientPermissionsError(BaseAPIException):
    def __init__(self):
        super().__init__(status_code=403, detail="权限不足")

# 在路由中使用
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = get_user_from_db(user_id)
    if not user:
        raise UserNotFoundError(user_id)
    return user
```

## 11. 项目组织与最佳实践

### 11.1 中间件实现

```python
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware

# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    request.state.request_id = str(uuid.uuid4())

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(
        "请求处理完成",
        extra={
            "request_id": request.state.request_id,
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "process_time": process_time
        }
    )

    return response

# 自定义中间件类
class CustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 前置处理
        response = await call_next(request)
        # 后置处理
        return response

app.add_middleware(CustomMiddleware)
```

### 11.2 配置管理

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "FastAPI 应用"
    database_url: str
    redis_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    cors_origins: list[str] = []

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

# 在依赖中使用
async def get_db_session(settings: Settings = Depends(get_settings)):
    # 数据库连接逻辑
    pass
```

### 11.3 结构化日志

```python
import structlog
import logging.config

# 结构化日志配置
logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(colors=False),
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": True,
        },
    },
})
```

### 11.4 健康检查与监控

```python
from datetime import datetime

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0"
    }

@app.get("/health/db")
async def health_check_db(session: SessionDep):
    try:
        session.exec(select(1))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="数据库不可用")
```

### 11.5 测试策略

```python
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

# 测试配置
@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def db_session():
    # 测试数据库会话
    pass

# 测试实现
@pytest.mark.asyncio
async def test_create_user(async_client: AsyncClient):
    response = await async_client.post("/users", json={"name": "test"})
    assert response.status_code == 201
```

## 运维部署考虑

### 生产环境清单

1. **安全性**：HTTPS、认证、授权、CORS
2. **性能**：异步模式、连接池、缓存
3. **可靠性**：健康检查、优雅关闭、错误处理
4. **可观测性**：日志、监控、追踪
5. **可扩展性**：水平扩展、负载均衡
6. **部署**：容器化、CI/CD、基础设施即代码

### 关键监控指标

- **响应时间监控**：P95、P99 延迟
- **错误率跟踪**：4xx、5xx 响应监控
- **资源利用率**：CPU、内存、磁盘使用
- **数据库性能**：查询性能、连接池
- **外部服务监控**：第三方 API 依赖

FastAPI 提供了构建生产级 API 的成熟生态系统，其对类型安全、自动文档和异步支持的重视使其成为现代可扩展应用的理想选择。通过遵循这些最佳实践，DevOps 团队可以构建和维护高性能、可靠的 FastAPI 应用程序。