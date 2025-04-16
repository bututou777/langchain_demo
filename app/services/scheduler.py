from datetime import datetime
from typing import TypedDict
import logging
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from app.config import settings

logger = logging.getLogger(__name__)

class TimeRange(TypedDict):
    start: str  # 格式 "HH:MM"
    end: str    # 格式 "HH:MM"

class ScheduleItem(TypedDict):
    start: str  # 格式 "HH:MM"
    end: str    # 格式 "HH:MM"
    task: str   # 任务名称或用餐
    description: str  # 任务描述和建议
    type: str   # "task" 或 "meal"

class ScheduleGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="qwen-plus",
            openai_api_key=settings.OPENAI_API_KEY,
            base_url='https://dashscope.aliyuncs.com/compatible-mode/v1',
            temperature=0.3
        )
        self.parser = JsonOutputParser()
        
        self.prompt = ChatPromptTemplate.from_template(
            """作为时间管理专家，请为以下任务在指定时间段内生成最优日程安排。

【可用时间】
{available_time_start} 到 {available_time_end}

【任务列表】
{tasks}

【用餐安排要求】
1. 早餐：建议在7:00-9:00之间安排30分钟
2. 午餐：建议在12:00-13:30之间安排60分钟
3. 晚餐：建议在18:00-19:30之间安排60分钟
注：仅在可用时间段内安排用餐时间

【优化原则】
1. 难度高的任务安排在认知高峰时段（上午9:00-11:00，下午14:00-16:00）
2. 相似任务批量处理，提高工作效率
3. 每工作90分钟安排15分钟休息
4. 合理分配任务，避免过度疲劳
5. 严格遵守用户设定的可用时间范围
6. 在可用时间段内适当安排用餐时间

请生成一个JSON数组，每个项目包含以下字段：
{{"start": "HH:MM", "end": "HH:MM", "task": "任务名称或用餐", "description": "具体的任务描述和建议", "type": "task或meal"}}

确保时间安排合理，任务之间有适当休息，输出格式严格符合要求。"""
        )

    async def generate(self, tasks: list, available_time: TimeRange) -> list[ScheduleItem]:
        try:
            task_descriptions = "\n".join(
                f"▪ {t.name} (难度{t.difficulty}/5，持续{t.duration}分钟)" 
                for t in tasks
            )
            
            logger.info(f"开始生成日程，任务数量：{len(tasks)}")
            logger.debug(f"可用时间：{available_time}")
            
            chain = self.prompt | self.llm | self.parser
            result = await chain.ainvoke({
                "tasks": task_descriptions,
                "available_time_start": available_time["start"],
                "available_time_end": available_time["end"],
                "current_time": datetime.now().strftime("%H:%M")
            })
            
            # 验证输出格式
            if not isinstance(result, list):
                raise ValueError("LLM返回格式错误：需要是数组")
            
            # 验证时间格式和顺序
            prev_end_time = None
            for item in result:
                if not all(key in item for key in ("start", "end", "task", "description", "type")):
                    raise ValueError("LLM返回的数据缺少必要字段")
                
                # 验证时间格式
                try:
                    start_time = datetime.strptime(item["start"], "%H:%M")
                    end_time = datetime.strptime(item["end"], "%H:%M")
                    
                    # 检查时间顺序
                    if start_time >= end_time:
                        raise ValueError(f"任务时间顺序错误: {item['task']} ({item['start']} -> {item['end']})")
                    
                    # 检查与前一个任务的时间间隔
                    if prev_end_time and start_time < prev_end_time:
                        raise ValueError(f"任务时间重叠: {item['task']}")
                    
                    prev_end_time = end_time
                except ValueError as e:
                    raise ValueError(f"时间格式验证失败: {str(e)}")
                
                # 验证类型字段
                if item["type"] not in ["task", "meal"]:
                    raise ValueError(f"无效的任务类型: {item['type']}")
            
            logger.info(f"日程生成成功，共{len(result)}个时间段")
            return result
            
        except Exception as e:
            logger.error(f"日程生成失败: {str(e)}")
            raise

async def generate_schedule(tasks, available_time):
    return await ScheduleGenerator().generate(tasks, available_time)
