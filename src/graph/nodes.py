import logging
import json
import json_repair
import logging
from copy import deepcopy
from typing import Literal
from langchain_core.messages import HumanMessage, BaseMessage

import json_repair
from langchain_core.messages import HumanMessage
from langgraph.types import Command

from src.agents import research_agent, coder_agent, browser_agent
from src.llms.llm import get_llm_by_type
from src.config import TEAM_MEMBERS
from src.config.agents import AGENT_LLM_MAP
from src.prompts.template import apply_prompt_template
from src.tools.search import tavily_tool
from src.utils.json_utils import repair_json_output
from .types import State, Router

# 设置日志记录器
logger = logging.getLogger(__name__)

# 定义统一的响应格式，将在所有代理返回结果时使用
# {}: 第一个占位符用于代理名称，第二个占位符用于代理的响应内容
RESPONSE_FORMAT = "Response from {}:\n\n<response>\n{}\n</response>\n\n*Please execute the next step.*"


def research_node(state: State) -> Command[Literal["supervisor"]]:
    """研究代理节点，负责执行研究任务。

    这个节点会调用research_agent来处理当前状态，并将结果格式化后返回给监督者节点。

    Args:
        state: 当前工作流状态，包含消息历史等信息

    Returns:
        Command对象，包含更新指令和下一步去向（固定返回supervisor节点）
    """
    logger.info("Research agent starting task")
    # 调用研究代理处理当前状态
    result = research_agent.invoke(state)
    logger.info("Research agent completed task")
    response_content = result["messages"][-1].content
    # 尝试修复可能的JSON输出
    response_content = repair_json_output(response_content)
    logger.debug(f"Research agent response: {response_content}")
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response_content,
                    name="researcher",
                )
            ]
        },
        goto="supervisor",
    )


def code_node(state: State) -> Command[Literal["supervisor"]]:
    """编程代理节点，负责执行Python代码相关任务。

    这个节点调用coder_agent来处理当前状态，执行代码写作、调试等任务，
    并将结果格式化后返回给监督者节点。

    Args:
        state: 当前工作流状态，包含消息历史等信息

    Returns:
        Command对象，包含更新指令和下一步去向（固定返回supervisor节点）
    """
    logger.info("Code agent starting task")
    # 调用编程代理处理当前状态
    result = coder_agent.invoke(state)
    logger.info("Code agent completed task")
    response_content = result["messages"][-1].content
    # 尝试修复可能的JSON输出
    response_content = repair_json_output(response_content)
    logger.debug(f"Code agent response: {response_content}")
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response_content,
                    name="coder",
                )
            ]
        },
        goto="supervisor",
    )


def browser_node(state: State) -> Command[Literal["supervisor"]]:
    """浏览器代理节点，负责执行网页浏览和交互任务。

    这个节点调用browser_agent来处理当前状态，执行网页访问、信息抓取等任务，
    并将结果格式化后返回给监督者节点。

    Args:
        state: 当前工作流状态，包含消息历史等信息

    Returns:
        Command对象，包含更新指令和下一步去向（固定返回supervisor节点）
    """
    logger.info("Browser agent starting task")
    # 调用浏览器代理处理当前状态
    result = browser_agent.invoke(state)
    logger.info("Browser agent completed task")
    response_content = result["messages"][-1].content
    # 尝试修复可能的JSON输出
    response_content = repair_json_output(response_content)
    logger.debug(f"Browser agent response: {response_content}")
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response_content,
                    name="browser",
                )
            ]
        },
        goto="supervisor",
    )


def supervisor_node(state: State) -> Command[Literal[*TEAM_MEMBERS, "__end__"]]:
    """监督者节点，负责决策下一步应该由哪个代理执行。

    这是整个工作流的核心控制器，它会根据当前状态评估并决定下一步行动：
    - 可能分配任务给团队成员之一(researcher, coder, browser, reporter)
    - 或者结束整个工作流(FINISH -> __end__)

    Args:
        state: 当前工作流状态，包含消息历史等信息

    Returns:
        Command对象，指示下一步转到哪个节点，以及状态更新
    """
    logger.info("Supervisor evaluating next action")
    # 应用监督者提示模板
    messages = apply_prompt_template("supervisor", state)
    # preprocess messages to make supervisor execute better.
    messages = deepcopy(messages)
    for message in messages:
        if isinstance(message, BaseMessage) and message.name in TEAM_MEMBERS:
            message.content = RESPONSE_FORMAT.format(message.name, message.content)
    response = (
        get_llm_by_type(AGENT_LLM_MAP["supervisor"])
        .with_structured_output(schema=Router, method="json_mode")
        .invoke(messages)
    )
    goto = response["next"]
    logger.debug(f"Current state messages: {state['messages']}")
    logger.debug(f"Supervisor response: {response}")

    # 处理特殊的"FINISH"指令，转换为langgraph的结束标记"__end__"
    if goto == "FINISH":
        goto = "__end__"
        logger.info("Workflow completed")
    else:
        logger.info(f"Supervisor delegating to: {goto}")

    # 创建Command对象，更新状态中的next字段并指示下一个节点
    return Command(goto=goto, update={"next": goto})


def planner_node(state: State) -> Command[Literal["supervisor", "__end__"]]:
    """计划者节点，负责生成完整的执行计划。

    这个节点生成整个任务的详细执行计划，支持以下高级功能：
    - 深度思考模式：使用更强大的推理型LLM
    - 搜索辅助计划：在规划前执行网络搜索以获取更多信息

    Args:
        state: 当前工作流状态，包含消息历史等信息

    Returns:
        Command对象，包含计划更新和下一步指示(通常是supervisor，失败则直接结束)
    """
    logger.info("Planner generating full plan")
    # 应用计划者提示模板
    messages = apply_prompt_template("planner", state)

    # 根据状态选择不同的LLM
    llm = get_llm_by_type("basic")
    if state.get("deep_thinking_mode"):
        # 如果启用深度思考模式，使用更强大的推理型LLM
        llm = get_llm_by_type("reasoning")

    # 如果启用了搜索辅助规划，先执行搜索
    if state.get("search_before_planning"):
        # 使用Tavily搜索工具基于用户最后一条消息执行搜索
        searched_content = tavily_tool.invoke({"query": state["messages"][-1].content})
        messages = deepcopy(messages)
        # 将搜索结果添加到提示中
        messages[
            -1
        ].content += f"\n\n# Relative Search Results\n\n{json.dumps([{'title': elem['title'], 'content': elem['content']} for elem in searched_content], ensure_ascii=False)}"

    # 流式调用LLM以获取响应
    stream = llm.stream(messages)
    full_response = ""
    for chunk in stream:
        full_response += chunk.content
    logger.debug(f"Current state messages: {state['messages']}")
    logger.debug(f"Planner response: {full_response}")

    # 清理响应格式，移除可能的代码块标记
    if full_response.startswith("```json"):
        full_response = full_response.removeprefix("```json")

    if full_response.endswith("```"):
        full_response = full_response.removesuffix("```")

    # 默认下一步是supervisor
    goto = "supervisor"
    # 验证返回的JSON是否有效
    try:
        repaired_response = json_repair.loads(full_response)
        full_response = json.dumps(repaired_response)
    except json.JSONDecodeError:
        # 如果解析失败，记录警告并结束流程
        logger.warning("Planner response is not a valid JSON")
        goto = "__end__"

    # 创建Command对象，更新消息和计划，并指示下一步
    return Command(
        update={
            "messages": [HumanMessage(content=full_response, name="planner")],
            "full_plan": full_response,
        },
        goto=goto,
    )


def coordinator_node(state: State) -> Command[Literal["planner", "__end__"]]:
    """协调者节点，负责与客户交流并决定是否需要规划。

    这个节点是与客户直接交互的接口，它会评估客户的请求并决定：
    - 直接结束会话
    - 或者转交给planner节点进行任务规划

    Args:
        state: 当前工作流状态，包含消息历史等信息

    Returns:
        Command对象，指示下一步(planner或__end__)
    """
    logger.info("Coordinator talking.")
    # 应用协调者提示模板
    messages = apply_prompt_template("coordinator", state)
    # 调用LLM获取响应
    response = get_llm_by_type(AGENT_LLM_MAP["coordinator"]).invoke(messages)
    logger.debug(f"Current state messages: {state['messages']}")
    response_content = response.content
    # 尝试修复可能的JSON输出
    response_content = repair_json_output(response_content)
    logger.debug(f"Coordinator response: {response_content}")

    # 默认是结束流程
    goto = "__end__"
    # 如果响应中包含特定标记，则转向planner
    if "handoff_to_planner" in response_content:
        goto = "planner"
    # 创建Command对象，指示下一步

    # 更新response.content为修复后的内容
    response.content = response_content

    return Command(
        goto=goto,
    )


def reporter_node(state: State) -> Command[Literal["supervisor"]]:
    """报告者节点，负责生成最终报告。

    这个节点会整合之前所有工作的结果，生成一份结构化的最终报告，
    并将结果返回给监督者节点进行下一步决策。

    Args:
        state: 当前工作流状态，包含消息历史等信息

    Returns:
        Command对象，包含报告更新和下一步去向(固定返回supervisor)
    """
    logger.info("Reporter write final report")
    # 应用报告者提示模板
    messages = apply_prompt_template("reporter", state)
    # 调用LLM获取响应
    response = get_llm_by_type(AGENT_LLM_MAP["reporter"]).invoke(messages)
    logger.debug(f"Current state messages: {state['messages']}")
    response_content = response.content
    # 尝试修复可能的JSON输出
    response_content = repair_json_output(response_content)
    logger.debug(f"reporter response: {response_content}")

    # 创建Command对象，更新消息并指示下一步转到supervisor节点
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response_content,
                    name="reporter",
                )
            ]
        },
        goto="supervisor",
    )
