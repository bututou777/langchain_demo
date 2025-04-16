from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
from app.services.scheduler import generate_schedule
from typing import List

# 配置日志
logger = logging.getLogger(__name__)

router = APIRouter()

class TaskItem(BaseModel):
    name: str
    difficulty: int
    duration: int
    dependencies: list[str] = []

class ScheduleRequest(BaseModel):
    tasks: List[TaskItem]
    availableTime: dict = {
        "start": "09:00",
        "end": "22:00"
    }

@router.post("/generate")
async def create_schedule(request: ScheduleRequest):
    try:
        if not request.tasks:
            raise ValueError("任务列表不能为空")
            
        # 验证时间格式
        for time_key in ["start", "end"]:
            time_str = request.availableTime[time_key]
            try:
                hours, minutes = map(int, time_str.split(":"))
                if not (0 <= hours <= 23 and 0 <= minutes <= 59):
                    raise ValueError
            except:
                raise ValueError(f"无效的时间格式: {time_str}，请使用HH:MM格式")
                
        # 确保开始时间早于结束时间
        if request.availableTime["start"] >= request.availableTime["end"]:
            raise ValueError("开始时间必须早于结束时间")
            
        return await generate_schedule(request.tasks, request.availableTime)
    except Exception as e:
        logger.error(f"生成失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"计划生成失败: {str(e)}"
        )