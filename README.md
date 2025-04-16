# 智能日程规划器

这是一个基于 FastAPI 和 LangChain 开发的智能日程规划系统，能够根据用户输入的任务自动生成合理的日程安排。

## 技术栈

### 后端
- **FastAPI**: 现代、快速的 Web 框架
- **LangChain**: AI 应用开发框架
- **Qwen**: 通义千问大语言模型
- **Pydantic**: 数据验证和设置管理
- **Uvicorn**: ASGI 服务器

### 前端
- **原生 JavaScript**: 实现交互功能
- **HTML5/CSS3**: 构建用户界面
- **响应式设计**: 适配不同设备屏幕

## 功能特点

- 🕒 自定义时间段设置
- 📝 灵活的任务管理
- 🎯 智能任务安排
  - 考虑任务难度
  - 自动安排休息时间
  - 合理的用餐时间安排
- 🎨 美观的用户界面
- 📱 响应式设计

## 安装和使用

1. 克隆项目

```bash
git clone <repository-url>
cd langchain_demo
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 环境配置

创建 `.env` 文件，添加以下配置：
```properties
OPENAI_API_KEY=你的API密钥
```

4. 启动服务

```bash
uvicorn app.main:app --reload --port 8088
```

5. 访问应用

在浏览器中打开 http://localhost:8088

## 使用说明

1. 设置可用时间范围
   - 选择一天中可用于安排任务的时间段

2. 添加任务
   - 输入任务名称
   - 选择任务难度（简单/中等/困难）
   - 设置预计持续时间

3. 生成日程
   - 点击"生成今日计划"按钮
   - 系统会自动生成优化的日程安排

## 系统架构

### 后端结构
```
app/
├── main.py          # 应用入口
├── config.py        # 配置管理
├── routers/         # 路由模块
│   └── schedule.py  # 日程相关接口
└── services/        # 业务逻辑
    └── scheduler.py # 日程生成服务
```

### 前端结构
```
frontend/
├── index.html      # 主页面
├── styles.css      # 样式表
└── app.js         # 交互逻辑
```

## API 接口

### 生成日程计划
- **端点**: `/api/schedule/generate`
- **方法**: POST
- **请求体**:
```json
{
  "tasks": [
    {
      "name": "任务名称",
      "difficulty": 1-5,
      "duration": "分钟数",
      "dependencies": []
    }
  ],
  "availableTime": {
    "start": "HH:MM",
    "end": "HH:MM"
  }
}
```

## 注意事项

- 确保 API 密钥配置正确
- 任务持续时间最少为 15 分钟
- 建议在指定的时间范围内合理安排任务数量
- 系统会自动考虑用餐时间和休息时间

## 开发计划

- [ ] 添加任务优先级设置
- [ ] 支持任务依赖关系
- [ ] 添加日程导出功能
- [ ] 集成日历同步功能
- [ ] 添加多语言支持

## 联系方式

如有问题或建议，欢迎提出 Issue 或 Pull Request。