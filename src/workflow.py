import logging
from src.config import TEAM_MEMBERS
from src.graph import build_graph

# 配置日志系统
logging.basicConfig(
    level=logging.INFO,  # 默认日志级别为INFO
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def enable_debug_logging():
    """启用调试级别日志，提供更详细的执行信息。"""
    logging.getLogger("src").setLevel(logging.DEBUG)


logger = logging.getLogger(__name__)

# 创建LangGraph工作流图
# 这是系统的核心组件，定义了各个代理之间的协作关系
graph = build_graph()


def run_agent_workflow(user_input: str, debug: bool = False):
    """运行代理工作流处理用户输入。

    工作流执行流程:
    1. 检查输入有效性
    2. 初始化日志级别
    3. 将用户输入转换为消息格式
    4. 使用预定义的图结构处理请求
    5. 返回最终工作流状态

    Args:
        user_input: 用户的查询或请求内容
        debug: 如果为True，启用调试级别日志

    Returns:
        工作流完成后的最终状态（包含所有消息历史和执行结果）

    Raises:
        ValueError: 当输入为空时抛出
    """
    if not user_input:
        raise ValueError("Input could not be empty")

    # 根据debug标志设置适当的日志级别
    if debug:
        enable_debug_logging()

    logger.info(f"Starting workflow with user input: {user_input}")

    # 调用工作流图处理请求
    # 初始状态包含:
    # 1. 团队成员列表(常量)
    # 2. 用户输入消息
    # 3. 工作流配置参数(深度思考模式和搜索辅助规划)
    result = graph.invoke(
        {
            # 常量配置
            "TEAM_MEMBERS": TEAM_MEMBERS,  # 所有可用的代理列表

            # 运行时变量
            "messages": [{"role": "user", "content": user_input}],  # 转换用户输入为消息格式
            "deep_thinking_mode": True,  # 启用深度思考模式，使用更强大的推理LLM
            "search_before_planning": True,  # 启用搜索辅助规划，在计划前执行相关搜索
        }
    )

    logger.debug(f"Final workflow state: {result}")
    logger.info("Workflow completed successfully")
    return result


if __name__ == "__main__":
    # 使用Mermaid格式可视化工作流图结构
    # 可以将输出复制到Mermaid在线编辑器查看图形化表示
    # https://mermaid-js.github.io/mermaid-live-editor/
    print(graph.get_graph().draw_mermaid())
