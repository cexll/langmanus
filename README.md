# LangManus - 多代理协作系统

LangManus是一个基于LangGraph构建的多代理协作系统，通过专业代理团队协作完成复杂任务。

## 项目架构

### 系统组件

1. **代理团队**
   - **协调者(Coordinator)**: 与用户交互，确定任务需求
   - **规划者(Planner)**: 生成详细的任务执行计划
   - **监督者(Supervisor)**: 分配任务给专业代理，控制工作流
   - **研究者(Researcher)**: 执行网络搜索和信息收集
   - **编码者(Coder)**: 编写和执行代码
   - **浏览器代理(Browser)**: 模拟浏览器交互，处理网页内容
   - **报告者(Reporter)**: 生成最终报告和结论

2. **工作流引擎**
   - 基于LangGraph构建的有向图工作流
   - 事件驱动的异步执行模式
   - 状态管理和流程控制

3. **语言模型集成**
   - **基础LLM(Basic)**: 用于一般任务处理
   - **推理LLM(Reasoning)**: 用于复杂思考和规划
   - **视觉LLM(Vision)**: 用于处理图像和网页内容

### 目录结构

```
src/
├── agents/             # 代理定义和实现
│   ├── agents.py       # 代理创建和配置
│   └── llm.py          # 语言模型接口
├── api/                # API接口
├── config/             # 配置文件
│   ├── agents.py       # 代理-LLM映射
│   └── env.py          # 环境变量配置
├── crawler/            # 网页爬取工具
├── graph/              # 工作流图定义
│   ├── builder.py      # 图构建器
│   ├── nodes.py        # 节点函数定义
│   └── types.py        # 状态和类型定义
├── prompts/            # 提示模板
├── service/            # 服务层
│   └── workflow_service.py  # 工作流服务
├── tools/              # 工具集合
└── workflow.py         # 主工作流入口
```

## 工作流程

1. **任务接收**
   - 用户提交请求到系统
   - Coordinator评估任务并与用户交互

2. **任务规划**
   - Planner生成详细执行计划
   - 可选择使用搜索增强和深度思考模式

3. **任务执行**
   - Supervisor根据计划分配任务
   - 专业代理执行分配的任务并返回结果
   - Supervisor评估结果并决定下一步

4. **任务完成**
   - Reporter汇总结果生成最终报告
   - 系统返回完整结果给用户

## 高级特性

1. **深度思考模式**
   - 使用更强大的推理型LLM处理复杂任务
   - 通过配置参数`deep_thinking_mode`启用

2. **搜索辅助规划**
   - 在生成计划前执行相关搜索
   - 通过配置参数`search_before_planning`启用

3. **事件流处理**
   - 流式处理代理执行过程
   - 实时返回执行状态和结果

## 使用示例

```python
from src.workflow import run_agent_workflow

# 运行工作流处理用户请求
result = run_agent_workflow(
    user_input="分析最近比特币价格变化并预测未来一周趋势",
    debug=True  # 启用调试模式
)

# 打印结果
print(result)
```

## 扩展和定制

1. **添加新代理**
   - 在`src/agents/agents.py`中定义新代理
   - 更新`src/config/agents.py`中的映射关系
   - 在`src/graph/builder.py`中添加新节点

2. **添加新工具**
   - 在`src/tools/`目录下创建新工具
   - 分配给适当的代理使用

3. **自定义提示模板**
   - 在`src/prompts/`目录下定义新模板
   - 通过`apply_prompt_template`函数应用

# LangManus

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![WeChat](https://img.shields.io/badge/WeChat-Langmanus-brightgreen?logo=wechat&logoColor=white)](./assets/wechat_community.jpg)
[![Discord Follow](https://dcbadge.vercel.app/api/server/m3MszDcn?style=flat)](https://discord.gg/m3MszDcn)

[English](./README.md) | [简体中文](./README_zh.md)

> Come From Open Source, Back to Open Source

LangManus is a community-driven AI automation framework that builds upon the incredible work of the open source community. Our goal is to combine language models with specialized tools for tasks like web search, crawling, and Python code execution, while giving back to the community that made this possible.

## Demo Video

> **Task**: Calculate the influence index of DeepSeek R1 on HuggingFace. This index can be designed by considering a weighted sum of factors such as followers, downloads, and likes.

[![Demo](./assets/demo.gif)](./assets/demo.mp4)

- [View on YouTube](https://youtu.be/sZCHqrQBUGk)
- [Download Video](https://github.com/langmanus/langmanus/blob/main/assets/demo.mp4)

## Table of Contents
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Features](#features)
- [Why LangManus?](#why-langmanus)
- [Setup](#setup)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Configuration](#configuration)
- [Usage](#usage)
- [Web UI](#web-ui)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Quick Start

```bash
# Clone the repository
git clone https://github.com/langmanus/langmanus.git
cd langmanus

# Install dependencies, uv will take care of the python interpreter and venv creation
uv sync

source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run the project
uv run main.py
```

## Architecture

LangManus implements a hierarchical multi-agent system where a supervisor coordinates specialized agents to accomplish complex tasks:

![LangManus Architecture](./assets/architecture.png)

The system consists of the following agents working together:

1. **Coordinator** - The entry point that handles initial interactions and routes tasks
2. **Planner** - Analyzes tasks and creates execution strategies
3. **Supervisor** - Oversees and manages the execution of other agents
4. **Researcher** - Gathers and analyzes information
5. **Coder** - Handles code generation and modifications
6. **Browser** - Performs web browsing and information retrieval
7. **Reporter** - Generates reports and summaries of the workflow results

## Features

### Core Capabilities
- 🤖 **LLM Integration**
    - Support for open source models like Qwen
    - OpenAI-compatible API interface
    - Multi-tier LLM system for different task complexities

### Tools and Integrations
- 🔍 **Search and Retrieval**
    - Web search via Tavily API
    - Neural search with Jina
    - Advanced content extraction

### Development Features
- 🐍 **Python Integration**
    - Built-in Python REPL
    - Code execution environment
    - Package management with uv

### Workflow Management
- 📊 **Visualization and Control**
    - Workflow graph visualization
    - Multi-agent orchestration
    - Task delegation and monitoring

## Why LangManus?

We believe in the power of open source collaboration. This project wouldn't be possible without the amazing work of projects like:
- [Qwen](https://github.com/QwenLM/Qwen) for their open source LLMs
- [Tavily](https://tavily.com/) for search capabilities
- [Jina](https://jina.ai/) for neural search technology
- And many other open source contributors

We're committed to giving back to the community and welcome contributions of all kinds - whether it's code, documentation, bug reports, or feature suggestions.

## Setup

### Prerequisites

- [uv](https://github.com/astral-sh/uv) package manager

### Installation

LangManus leverages [uv](https://github.com/astral-sh/uv) as its package manager to streamline dependency management.
Follow the steps below to set up a virtual environment and install the necessary dependencies:

```bash
# Step 1: Create and activate a virtual environment through uv
uv python install 3.12
uv venv --python 3.12

source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Step 2: Install project dependencies
uv sync
```

By completing these steps, you'll ensure your environment is properly configured and ready for development.

### Configuration

LangManus uses a three-tier LLM system with separate configurations for reasoning, basic tasks, and vision-language tasks. Create a `.env` file in the project root and configure the following environment variables:

```ini
# Reasoning LLM Configuration (for complex reasoning tasks)
REASONING_MODEL=your_reasoning_model
REASONING_API_KEY=your_reasoning_api_key
REASONING_BASE_URL=your_custom_base_url  # Optional

# Basic LLM Configuration (for simpler tasks)
BASIC_MODEL=your_basic_model
BASIC_API_KEY=your_basic_api_key
BASIC_BASE_URL=your_custom_base_url  # Optional

# Vision-Language LLM Configuration (for tasks involving images)
VL_MODEL=your_vl_model
VL_API_KEY=your_vl_api_key
VL_BASE_URL=your_custom_base_url  # Optional

# Tool API Keys
TAVILY_API_KEY=your_tavily_api_key
JINA_API_KEY=your_jina_api_key  # Optional

# Browser Configuration
CHROME_INSTANCE_PATH=/Applications/Google Chrome.app/Contents/MacOS/Google Chrome  # Optional, path to Chrome executable
```

In addition to supporting LLMs compatible with OpenAI, LangManus also supports Azure LLMs. The configuration method is as follows:
```ini
# AZURE LLM Config
AZURE_API_BASE=https://xxxx
AZURE_API_KEY=xxxxx
AZURE_API_VERSION=2023-07-01-preview

# Reasoning LLM (for complex reasoning tasks)
REASONING_AZURE_DEPLOYMENT=xxx

# Non-reasoning LLM (for straightforward tasks)
BASIC_AZURE_DEPLOYMENT=gpt-4o-2024-08-06

# Vision-language LLM (for tasks requiring visual understanding)
VL_AZURE_DEPLOYMENT=gpt-4o-2024-08-06
```

> **Note:**
>
> - The system uses different models for different types of tasks:
>     - Reasoning LLM for complex decision-making and analysis
>     - Basic LLM for simpler text-based tasks
>     - Vision-Language LLM for tasks involving image understanding
> - You can customize the base URLs for all LLMs independently, and you can use LiteLLM's board LLM support by following [this guide](https://docs.litellm.ai/docs/providers).
> - Each LLM can use different API keys if needed
> - Jina API key is optional. Provide your own key to access a higher rate limit (get your API key at [jina.ai](https://jina.ai/))
> - Tavily search is configured to return a maximum of 5 results by default (get your API key at [app.tavily.com](https://app.tavily.com/))

You can copy the `.env.example` file as a template to get started:

```bash
cp .env.example .env
```

### Configure Pre-commit Hook
LangManus includes a pre-commit hook that runs linting and formatting checks before each commit. To set it up:

1. Make the pre-commit script executable:
```bash
chmod +x pre-commit
```

2. Install the pre-commit hook:
```bash
ln -s ../../pre-commit .git/hooks/pre-commit
```

The pre-commit hook will automatically:
- Run linting checks (`make lint`)
- Run code formatting (`make format`)
- Add any reformatted files back to staging
- Prevent commits if there are any linting or formatting errors

## Usage

### Basic Execution

To run LangManus with default settings:

```bash
uv run main.py
```

### API Server

LangManus provides a FastAPI-based API server with streaming support:

```bash
# Start the API server
make serve

# Or run directly
uv run server.py
```

The API server exposes the following endpoints:

- `POST /api/chat/stream`: Chat endpoint for LangGraph invoke with streaming support
    - Request body:
    ```json
    {
      "messages": [
        {"role": "user", "content": "Your query here"}
      ],
      "debug": false
    }
    ```
    - Returns a Server-Sent Events (SSE) stream with the agent's responses

### Advanced Configuration

LangManus can be customized through various configuration files in the `src/config` directory:
- `env.py`: Configure LLM models, API keys, and base URLs
- `tools.py`: Adjust tool-specific settings (e.g., Tavily search results limit)
- `agents.py`: Modify team composition and agent system prompts

### Agent Prompts System

LangManus uses a sophisticated prompting system in the `src/prompts` directory to define agent behaviors and responsibilities:

#### Core Agent Roles

- **Supervisor ([`src/prompts/supervisor.md`](src/prompts/supervisor.md))**: Coordinates the team and delegates tasks by analyzing requests and determining which specialist should handle them. Makes decisions about task completion and workflow transitions.

- **Researcher ([`src/prompts/researcher.md`](src/prompts/researcher.md))**: Specializes in information gathering through web searches and data collection. Uses Tavily search and web crawling capabilities while avoiding mathematical computations or file operations.

- **Coder ([`src/prompts/coder.md`](src/prompts/coder.md))**: Professional software engineer role focused on Python and bash scripting. Handles:
    - Python code execution and analysis
    - Shell command execution
    - Technical problem-solving and implementation

- **File Manager ([`src/prompts/file_manager.md`](src/prompts/file_manager.md))**: Handles all file system operations with a focus on properly formatting and saving content in markdown format.

- **Browser ([`src/prompts/browser.md`](src/prompts/browser.md))**: Web interaction specialist that handles:
    - Website navigation
    - Page interaction (clicking, typing, scrolling)
    - Content extraction from web pages

#### Prompt System Architecture

The prompts system uses a template engine ([`src/prompts/template.py`](src/prompts/template.py)) that:
- Loads role-specific markdown templates
- Handles variable substitution (e.g., current time, team member information)
- Formats system prompts for each agent

Each agent's prompt is defined in a separate markdown file, making it easy to modify behavior and responsibilities without changing the underlying code.

## Web UI

LangManus provides a default web UI.

Please refer to the [langmanus/langmanus-web-ui](https://github.com/langmanus/langmanus-web) project for more details.

## Development

### Testing

Run the test suite:

```bash
# Run all tests
make test

# Run specific test file
pytest tests/integration/test_workflow.py

# Run with coverage
make coverage
```

### Code Quality

```bash
# Run linting
make lint

# Format code
make format
```

## Contributing

We welcome contributions of all kinds! Whether you're fixing a typo, improving documentation, or adding a new feature, your help is appreciated. Please see our [Contributing Guide](CONTRIBUTING.md) for details on how to get started.

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

Special thanks to all the open source projects and contributors that make LangManus possible. We stand on the shoulders of giants.
