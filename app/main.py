from fastapi import FastAPI
from app.routers import schedule
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI()

# 更新CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:8000"],  # 允许本地前端访问
    allow_credentials=True,  # 允许携带凭证
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],
)

# 路由注册
app.include_router(schedule.router, prefix="/api/schedule", tags=["schedule"])

# 挂载前端文件（假设前端文件在项目根目录的 frontend 文件夹）
try:
    app.mount("/", StaticFiles(directory="./frontend", html=True), name="frontend")
    logger.info("前端文件挂载成功")
except Exception as e:
    logger.error(f"前端文件挂载失败: {str(e)}")

@app.on_event("startup")
async def startup_event():
    logger.info("应用程序启动")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("应用程序关闭")
