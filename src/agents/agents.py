from langgraph.prebuilt import create_react_agent

from src.prompts import apply_prompt_template
from src.tools import (
    bash_tool,  # 执行Shell命令的工具
    browser_tool,  # 网页浏览和交互工具
    crawl_tool,  # 网页爬取工具
    python_repl_tool,  # Python代码执行工具
    tavily_tool,  # Tavily搜索引擎工具
)

from src.llms.llm import get_llm_by_type
from src.config.agents import AGENT_LLM_MAP

# 创建各种专家代理
# ReAct代理：使用"思考-行动-观察"模式处理任务，可以使用各种工具

# 1. 研究代理 - 负责信息搜索和调研
# 工具:
# - tavily_tool: 用于进行网络搜索，获取最新信息
# - crawl_tool: 用于抓取和分析网页内容
research_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP["researcher"]),  # 使用配置的LLM类型
    tools=[tavily_tool, crawl_tool],  # 提供研究工具
    prompt=lambda state: apply_prompt_template("researcher", state),  # 使用特定提示模板
)

# 2. 编码代理 - 负责编写和执行代码
# 工具:
# - python_repl_tool: 允许执行Python代码并获取结果
# - bash_tool: 允许执行shell命令操作系统
coder_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP["coder"]),  # 使用配置的LLM类型
    tools=[python_repl_tool, bash_tool],  # 提供编码工具
    prompt=lambda state: apply_prompt_template("coder", state),  # 使用特定提示模板
)

# 3. 浏览器代理 - 负责网页浏览和交互
# 工具:
# - browser_tool: 允许模拟浏览器行为，如打开网页、点击链接、填写表单等
# 注意: 这个代理使用视觉语言模型(VLM)来处理网页内容
browser_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP["browser"]),  # 使用视觉语言模型
    tools=[browser_tool],  # 提供浏览器工具
    prompt=lambda state: apply_prompt_template("browser", state),  # 使用特定提示模板
)
