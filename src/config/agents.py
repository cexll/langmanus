from typing import Literal

# 定义可用的LLM类型
# basic: 基础语言模型，用于一般任务
# reasoning: 高级推理语言模型，用于复杂规划和推理
# vision: 视觉语言模型，可以处理图像和网页内容
LLMType = Literal["basic", "reasoning", "vision"]

# 定义代理-LLM映射关系
# 这个映射决定了每个代理使用哪种类型的语言模型
AGENT_LLM_MAP: dict[str, LLMType] = {
    "coordinator": "basic",  # 协调者使用基础LLM，负责与用户交互和任务分配
    "planner": "reasoning",  # 计划者使用推理型LLM，负责复杂任务分解和规划
    "supervisor": "basic",  # 监督者使用基础LLM，负责决策和任务分配
    "researcher": "basic",  # 研究者使用基础LLM，负责信息搜索和分析
    "coder": "basic",  # 编码者使用基础LLM，负责代码生成和执行
    "browser": "vision",  # 浏览器代理使用视觉LLM，负责网页交互和内容理解
    "reporter": "basic",  # 报告者使用基础LLM，负责总结和报告生成
}
