// ==================== 全局变量 ====================
let tasks = [];

// 页面加载时从 localStorage 恢复任务列表
document.addEventListener('DOMContentLoaded', () => {
    // 恢复保存的任务
    const savedTasks = localStorage.getItem('schedulerTasks');
    if (savedTasks) {
        tasks = JSON.parse(savedTasks);
        renderTaskList();
    }

    // 绑定事件监听器
    document.getElementById('addTaskBtn').addEventListener('click', addTask);
    document.getElementById('generateBtn').addEventListener('click', generateSchedule);
    document.getElementById('clearTasksBtn').addEventListener('click', clearTasks);
    
    // 输入框回车支持
    document.getElementById('taskName').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') addTask();
    });

    // 时间输入验证
    document.getElementById('availableTimeStart').addEventListener('change', validateTimeRange);
    document.getElementById('availableTimeEnd').addEventListener('change', validateTimeRange);
});

// ==================== 核心功能函数 ====================

/**
 * 验证时间范围
 */
function validateTimeRange() {
    const startTime = document.getElementById('availableTimeStart').value;
    const endTime = document.getElementById('availableTimeEnd').value;

    if (startTime && endTime && startTime >= endTime) {
        showError('结束时间必须晚于开始时间');
        document.getElementById('generateBtn').disabled = true;
        return false;
    }
    
    document.getElementById('generateBtn').disabled = false;
    return true;
}

/**
 * 保存任务到 localStorage
 */
function saveTasks() {
    localStorage.setItem('schedulerTasks', JSON.stringify(tasks));
}

/**
 * 清空所有任务
 */
function clearTasks() {
    if (tasks.length === 0) return;
    
    if (confirm('确定要清空所有任务吗？')) {
        tasks = [];
        localStorage.removeItem('schedulerTasks');
        renderTaskList();
        document.getElementById('scheduleResult').innerHTML = '';
    }
}

/**
 * 添加新任务
 */
function addTask() {
    const taskName = document.getElementById('taskName').value.trim();
    const duration = parseInt(document.getElementById('taskDuration').value);
    
    // 输入验证
    if (!taskName) {
        showError('任务名称不能为空');
        return;
    }
    if (isNaN(duration) || duration < 15) {
        showError('时长需要 ≥15分钟');
        return;
    }

    const newTask = {
        name: taskName,
        difficulty: parseInt(document.getElementById('taskDifficulty').value),
        duration: duration,
        dependencies: []
    };

    tasks.push(newTask);
    saveTasks(); // 保存到 localStorage
    renderTaskList();
    clearInputs();
}

/**
 * 删除任务
 */
function removeTask(index) {
    tasks = tasks.filter((_, i) => i !== index);
    saveTasks(); // 保存到 localStorage
    renderTaskList();
}

/**
 * 生成日程计划
 */
async function generateSchedule() {
    if (tasks.length === 0) {
        showError('请至少添加一个任务');
        return;
    }

    if (!validateTimeRange()) {
        return;
    }

    try {
        showLoading(true);
        document.getElementById('scheduleResult').innerHTML = '<div class="loading-message">🤔 正在思考最佳日程安排...</div>';
        console.log('正在发送请求，任务数据：', tasks);
        
        const response = await fetch('http://localhost:8088/api/schedule/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                tasks: tasks,
                availableTime: {
                    start: document.getElementById('availableTimeStart').value,
                    end: document.getElementById('availableTimeEnd').value
                }
            })
        });

        console.log('服务器响应状态：', response.status);
        
        if (!response.ok) {
            throw new Error(response.status === 500 ? '服务器内部错误' : '请求失败');
        }

        const schedule = await response.json();
        if (!Array.isArray(schedule)) {
            throw new Error('服务器返回数据格式错误');
        }

        console.log('收到服务器返回数据：', schedule);
        renderSchedule(schedule);
    } catch (error) {
        console.error('请求失败：', error);
        showError(error.message || '生成计划失败，请稍后重试');
        document.getElementById('scheduleResult').innerHTML = '';
    } finally {
        showLoading(false);
    }
}

// ==================== 渲染函数 ====================

/**
 * 渲染任务列表
 */
function renderTaskList() {
    const container = document.getElementById('taskList');
    container.innerHTML = tasks.map((task, index) => `
        <div class="task-item">
            <div>
                <span class="task-name">${task.name}</span>
                <span class="difficulty-badge">${getDifficultyBadge(task.difficulty)}</span>
                <span class="duration">${task.duration}分钟</span>
            </div>
            <button class="delete-btn" onclick="removeTask(${index})">🗑️ 删除</button>
        </div>
    `).join('');
}

/**
 * 渲染生成的日程
 */
function renderSchedule(schedule) {
    const container = document.getElementById('scheduleResult');
    container.innerHTML = schedule.map(item => `
        <div class="schedule-block ${item.type === 'meal' ? 'meal' : ''}">
            <div class="time-range">
                <span class="time">${item.start}</span>
                <span class="separator">→</span>
                <span class="time">${item.end}</span>
            </div>
            <div class="task-info">
                <h3 class="task-title">
                    ${item.type === 'meal' ? '🍽️ ' : '📝 '}${item.task}
                </h3>
                <p class="task-desc">${item.description}</p>
            </div>
        </div>
    `).join('');
}

// ==================== 辅助函数 ====================

/**
 * 显示难度标签
 */
function getDifficultyBadge(difficulty) {
    const levels = {
        1: '<span class="easy">简单</span>',
        3: '<span class="medium">中等</span>',
        5: '<span class="hard">困难</span>'
    };
    return levels[difficulty] || '<span class="unknown">未知</span>';
}

/**
 * 显示加载状态
 */
function showLoading(isLoading) {
    const btn = document.getElementById('generateBtn');
    btn.disabled = isLoading;
    btn.innerHTML = isLoading ? 
        '<div class="loader"></div> 生成中...' : 
        '🚀 生成今日计划';
}

/**
 * 显示错误信息
 */
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = `⚠️ ${message}`;
    
    document.body.appendChild(errorDiv);
    setTimeout(() => errorDiv.remove(), 3000);
}

/**
 * 清空输入框
 */
function clearInputs() {
    document.getElementById('taskName').value = '';
    document.getElementById('taskDuration').value = '60';
}
