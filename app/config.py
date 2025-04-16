from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
from pathlib import Path

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 加载环境变量
env_path = BASE_DIR / '.env'
load_dotenv(env_path)

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    
    class Config:
        env_file = str(env_path)
        extra = 'allow'

settings = Settings()
