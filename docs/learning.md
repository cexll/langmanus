# LangManus 项目学习指南

## 项目背景
LangManus 是一个基于 LangChain 和 LangGraph 的 AI Agent 项目，集成了多种现代化工具和技术，用于构建智能代理系统。该项目展示了如何构建一个完整的 AI Agent 系统，包括工作流编排、工具集成、API 服务等多个方面。

## 技术栈

### 1. 核心框架
- **LangChain 生态系统**
  - langchain-community
  - langchain-experimental
  - langchain-openai
  - langgraph
  - langchain-deepseek
- **LiteLLM**: LLM 模型管理
- **FastAPI**: Web 框架
- **Uvicorn**: ASGI 服务器

### 2. 数据处理
- **Pandas & NumPy**: 数据处理和分析
- **yfinance**: 金融数据获取
- **readabilipy**: 网页内容解析
- **markdownify**: Markdown 处理

### 3. 开发工具
- Python 3.12+
- pytest: 测试框架
- black: 代码格式化
- python-dotenv: 环境变量管理

## 项目结构

```tree
src/
├── agents/     # Agent 实现
├── graph/      # LangGraph 工作流定义
├── prompts/    # 提示词模板
├── tools/      # Agent 工具集
├── service/    # 服务层实现
├── api/        # API 接口
├── crawler/    # 数据爬取
├── config/     # 配置管理
└── workflow.py # 工作流程编排
```

## 学习路径规划

### 1. 基础阶段
- **环境搭建**
  - Python 3.12 环境配置
  - 项目依赖安装
  - 配置文件设置

- **核心概念学习**
  - 学习 LangChain 基础概念
  - 理解 LangGraph 工作流
  - 熟悉 AI Agent 架构

### 2. 进阶阶段
1. **提示词工程**
   - 研究 `prompts/` 目录
   - 学习提示词模板设计
   - 理解提示词优化技巧

2. **工具开发**
   - 分析 `tools/` 目录
   - 学习工具实现方式
   - 实践工具集成方法

3. **Agent 实现**
   - 深入 `agents/` 目录
   - 理解 Agent 设计模式
   - 掌握 Agent 交互逻辑

4. **工作流编排**
   - 研究 `graph/` 目录
   - 学习 LangGraph 使用
   - 理解工作流程设计

### 3. 实战阶段
1. **系统集成**
   - 学习 `service/` 实现
   - 研究 API 设计
   - 理解系统架构

2. **数据处理**
   - 分析 `crawler/` 模块
   - 学习数据获取方法
   - 掌握数据处理流程

3. **项目实践**
   - 修改现有功能
   - 添加新的工具
   - 优化工作流程

## 学习建议

### 1. 入门建议
- 先运行项目，熟悉基本功能
- 阅读项目文档和代码注释
- 从简单的模块开始理解

### 2. 进阶建议
- 深入研究 `workflow.py` 的实现
- 理解 Agent 间的交互逻辑
- 学习工作流编排方式
- 研究测试用例编写

### 3. 实战建议
- 尝试修改现有功能
- 添加新的 Agent 工具
- 优化提示词模板
- 编写完整的测试用例

## 项目优势
1. 使用最新技术栈
2. 完整的项目结构
3. 实际应用场景
4. 良好的工程实践
5. 完整的测试覆盖

## 注意事项
1. 确保 Python 版本兼容性 (3.12+)
2. 正确配置环境变量
3. 理解 LLM API 的使用限制
4. 遵循项目的代码规范
5. 注意测试用例的完整性
