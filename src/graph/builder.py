from langgraph.graph import StateGraph, START

from .types import State
from .nodes import (
    supervisor_node,
    research_node,
    code_node,
    coordinator_node,
    browser_node,
    reporter_node,
    planner_node,
)


def build_graph():
    """构建并返回代理工作流图。

    LangGraph工作流程结构:
    1. 工作流从START开始，首先进入coordinator协调者
    2. 协调者评估任务并可能将任务移交给planner规划者
    3. 规划者生成完整计划后交给supervisor监督者
    4. 监督者根据情况调度其他专家代理（研究员、编码者、浏览器代理、报告员）
    5. 每个专家代理完成任务后返回给supervisor监督者
    6. 监督者根据情况可能结束工作流或分配新任务

    返回:
        编译好的LangGraph工作流图
    """
    # 创建一个状态图，使用State类型作为状态定义
    builder = StateGraph(State)

    # 设置流程入口: 从START开始到coordinator节点
    builder.add_edge(START, "coordinator")

    # 添加各类节点:

    # 1. 协调者节点 - 与用户交互并决定是否需要规划
    builder.add_node("coordinator", coordinator_node)

    # 2. 规划者节点 - 生成完整的任务执行计划
    builder.add_node("planner", planner_node)

    # 3. 监督者节点 - 中央控制器，根据情况分配任务给不同代理
    builder.add_node("supervisor", supervisor_node)

    # 4. 研究者节点 - 执行信息搜索和研究任务
    builder.add_node("researcher", research_node)

    # 5. 编码者节点 - 执行代码相关任务
    builder.add_node("coder", code_node)

    # 6. 浏览器节点 - 执行网页浏览和交互任务
    builder.add_node("browser", browser_node)

    # 7. 报告者节点 - 生成最终报告和结论
    builder.add_node("reporter", reporter_node)

    # 编译图并返回可执行的工作流
    return builder.compile()
