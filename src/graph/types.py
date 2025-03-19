from typing import Literal
from typing_extensions import TypedDict
from langgraph.graph import MessagesState

from src.config import TEAM_MEMBERS

# 定义路由选项：可以路由到任意团队成员或结束工作流
OPTIONS = TEAM_MEMBERS + ["FINISH"]


class Router(TypedDict):
    """工作节点路由器，用于决定下一步执行哪个节点。

    这个类型由supervisor节点使用，来确定下一个应该执行的代理。
    如果没有需要执行的代理，则路由到"FINISH"结束工作流。

    Attributes:
        next: 下一个需要执行的节点名称，或"FINISH"表示完成
    """

    next: Literal[*OPTIONS]  # 使用Literal类型确保只能路由到预定义的选项


class State(MessagesState):
    """代理系统的状态定义，继承自MessagesState并添加了额外字段。

    这个类定义了整个工作流图的状态结构，包括:
    1. 消息历史 (从MessagesState继承)
    2. 常量配置
    3. 运行时变量

    Attributes:
        TEAM_MEMBERS: 团队成员列表常量
        next: 当前/下一个执行的节点
        full_plan: 由planner生成的完整计划(JSON格式)
        deep_thinking_mode: 是否启用深度思考模式(使用更强大的推理LLM)
        search_before_planning: 是否在规划前执行相关搜索
    """

    # 常量
    TEAM_MEMBERS: list[str]  # 可用的团队成员列表

    # 运行时变量
    next: str  # 当前/下一个执行节点
    full_plan: str  # 完整计划(JSON格式)
    deep_thinking_mode: bool  # 是否启用深度思考模式
    search_before_planning: bool  # 是否在规划前搜索
