import logging

from src.config import TEAM_MEMBERS
from src.graph import build_graph
from langchain_community.adapters.openai import convert_message_to_dict
import uuid

# 配置基础日志系统
logging.basicConfig(
    level=logging.INFO,  # 默认日志级别为INFO
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def enable_debug_logging():
    """启用调试级别日志，提供更详细的执行信息。

    这个函数将src包的日志级别设置为DEBUG，便于开发者排查问题。
    """
    logging.getLogger("src").setLevel(logging.DEBUG)


# 获取当前模块的日志记录器
logger = logging.getLogger(__name__)

# 创建代理工作流图
graph = build_graph()

# 协调者消息缓存，用于特殊处理协调者的输出
coordinator_cache = []
MAX_CACHE_SIZE = 3  # 最大缓存大小


async def run_agent_workflow(
    user_input_messages: list,
    debug: bool = False,
    deep_thinking_mode: bool = False,
    search_before_planning: bool = False,
):
    """运行代理工作流处理用户输入。

    这是系统的主要入口点，负责：
    1. 初始化工作流状态
    2. 处理工作流事件流
    3. 生成客户端可用的事件流

    Args:
        user_input_messages: 用户请求消息列表
        debug: 如果为True，启用调试级别日志
        deep_thinking_mode: 是否启用深度思考模式（使用更强大的推理LLM）
        search_before_planning: 是否在规划前执行搜索

    Returns:
        异步生成器，产生工作流执行过程中的各类事件

    Raises:
        ValueError: 当输入消息为空时抛出
    """
    if not user_input_messages:
        raise ValueError("Input could not be empty")

    # 如果开启调试模式，启用详细日志
    if debug:
        enable_debug_logging()

    logger.info(f"Starting workflow with user input: {user_input_messages}")

    # 为每次工作流生成唯一ID
    workflow_id = str(uuid.uuid4())

    # 定义需要流式输出的代理列表
    streaming_llm_agents = [*TEAM_MEMBERS, "planner", "coordinator"]

    # 在每次工作流开始时重置协调者缓存
    global coordinator_cache
    coordinator_cache = []
    global is_handoff_case
    is_handoff_case = False

    # 开始异步流式执行工作流图
    # TODO: extract message content from object, specifically for on_chat_model_stream
    async for event in graph.astream_events(
        {
            # 常量
            "TEAM_MEMBERS": TEAM_MEMBERS,
            # 运行时变量
            "messages": user_input_messages,  # 用户输入消息
            "deep_thinking_mode": deep_thinking_mode,  # 是否使用更强大的推理模型
            "search_before_planning": search_before_planning,  # 是否在规划前执行搜索
        },
        version="v2",  # 使用v2版本的事件流API
    ):
        # 解析事件信息
        kind = event.get("event")  # 事件类型
        data = event.get("data")   # 事件数据
        name = event.get("name")   # 事件名称
        metadata = event.get("metadata")  # 元数据

        # 从元数据中提取节点名称和步骤信息
        node = (
            ""
            if (metadata.get("checkpoint_ns") is None)
            else metadata.get("checkpoint_ns").split(":")[0]
        )
        langgraph_step = (
            ""
            if (metadata.get("langgraph_step") is None)
            else str(metadata["langgraph_step"])
        )
        run_id = "" if (event.get("run_id") is None) else str(event["run_id"])

        # 处理链开始事件 - 当代理开始工作时
        if kind == "on_chain_start" and name in streaming_llm_agents:
            # 特殊处理planner代理开始事件 - 标记整个工作流的开始
            if name == "planner":
                yield {
                    "event": "start_of_workflow",
                    "data": {"workflow_id": workflow_id, "input": user_input_messages},
                }
            # 生成代理开始事件
            ydata = {
                "event": "start_of_agent",
                "data": {
                    "agent_name": name,
                    "agent_id": f"{workflow_id}_{name}_{langgraph_step}",
                },
            }
        # 处理链结束事件 - 当代理完成工作时
        elif kind == "on_chain_end" and name in streaming_llm_agents:
            ydata = {
                "event": "end_of_agent",
                "data": {
                    "agent_name": name,
                    "agent_id": f"{workflow_id}_{name}_{langgraph_step}",
                },
            }
        # 处理LLM开始事件 - 当语言模型开始生成时
        elif kind == "on_chat_model_start" and node in streaming_llm_agents:
            ydata = {
                "event": "start_of_llm",
                "data": {"agent_name": node},
            }
        # 处理LLM结束事件 - 当语言模型完成生成时
        elif kind == "on_chat_model_end" and node in streaming_llm_agents:
            ydata = {
                "event": "end_of_llm",
                "data": {"agent_name": node},
            }
        # 处理LLM流式输出事件 - 处理模型生成的每个文本块
        elif kind == "on_chat_model_stream" and node in streaming_llm_agents:
            content = data["chunk"].content
            # 处理空内容或特殊的推理内容
            if content is None or content == "":
                if not data["chunk"].additional_kwargs.get("reasoning_content"):
                    # 跳过完全空的消息
                    continue
                # 处理包含推理内容的消息
                ydata = {
                    "event": "message",
                    "data": {
                        "message_id": data["chunk"].id,
                        "delta": {
                            "reasoning_content": (
                                data["chunk"].additional_kwargs["reasoning_content"]
                            )
                        },
                    },
                }
            else:
                # 特殊处理协调者的消息
                if node == "coordinator":
                    # 实现协调者消息的缓存逻辑，用于检测特殊指令
                    if len(coordinator_cache) < MAX_CACHE_SIZE:
                        coordinator_cache.append(content)
                        cached_content = "".join(coordinator_cache)
                        # 检查是否为移交给planner的特殊指令
                        if cached_content.startswith("handoff"):
                            is_handoff_case = True
                            continue
                        # 如果缓存未满，继续收集而不输出
                        if len(coordinator_cache) < MAX_CACHE_SIZE:
                            continue
                        # 缓存已满，发送完整缓存内容
                        ydata = {
                            "event": "message",
                            "data": {
                                "message_id": data["chunk"].id,
                                "delta": {"content": cached_content},
                            },
                        }
                    # 非移交情况且缓存已满，直接发送新内容
                    elif not is_handoff_case:
                        ydata = {
                            "event": "message",
                            "data": {
                                "message_id": data["chunk"].id,
                                "delta": {"content": content},
                            },
                        }
                else:
                    # 对其他代理，直接发送消息内容
                    ydata = {
                        "event": "message",
                        "data": {
                            "message_id": data["chunk"].id,
                            "delta": {"content": content},
                        },
                    }
        # 处理工具调用开始事件
        elif kind == "on_tool_start" and node in TEAM_MEMBERS:
            ydata = {
                "event": "tool_call",
                "data": {
                    "tool_call_id": f"{workflow_id}_{node}_{name}_{run_id}",
                    "tool_name": name,
                    "tool_input": data.get("input"),
                },
            }
        # 处理工具调用结束事件
        elif kind == "on_tool_end" and node in TEAM_MEMBERS:
            ydata = {
                "event": "tool_call_result",
                "data": {
                    "tool_call_id": f"{workflow_id}_{node}_{name}_{run_id}",
                    "tool_name": name,
                    "tool_result": data["output"].content if data.get("output") else "",
                },
            }
        else:
            # 跳过其他类型的事件
            continue

        # 将处理后的事件发送给客户端
        yield ydata

    # 特殊处理移交情况的工作流结束事件
    if is_handoff_case:
        # TODO: remove messages attributes after Frontend being compatible with final_session_state event.
        yield {
            "event": "end_of_workflow",
            "data": {
                "workflow_id": workflow_id,
                "messages": [
                    convert_message_to_dict(msg)
                    for msg in data["output"].get("messages", [])
                ],
            },
        }
    yield {
        "event": "final_session_state",
        "data": {
            "messages": [
                convert_message_to_dict(msg)
                for msg in data["output"].get("messages", [])
            ],
        },
    }
