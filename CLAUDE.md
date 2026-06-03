# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概览

这是一个基于智谱 `zai-sdk` 的轻量 Agent 示例项目，当前包含三类入口：

| 类型 | 说明 |
|---|---|
| 基础调用 demo | 直接调用智谱 SDK |
| 单 Agent demo | 售后客服场景，展示工具调用与 ReAct 循环 |
| 多 Agent demo | Master-Worker 编排，展示任务拆解、分发与汇总 |

代码主要分为 4 层：

| 层级 | 路径 | 作用 |
|---|---|---|
| LLM 基础层 | `src/llm/` | 封装模型调用、system prompt 注入、结构化输出校验 |
| Prompt 工具层 | `src/prompts/` | 提供多行 prompt 的统一缩进清理方法 |
| Agent 层 | `src/my_agent/` | 实现单 Agent 与多 Agent 编排逻辑 |
| Demo 层 | `demos/` | 提供可直接运行的示例入口 |

## 环境与依赖

常用初始化命令：

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

运行时环境变量：

| 变量 | 说明 |
|---|---|
| `ZAI_API_KEY` | 智谱 API Key，必需 |
| `ZAI_MODEL` | 调用模型名，`BaseLLMCaller` 会读取 |
| `USER_ID` | demo 中获取用户信息时会读取，非必需 |

## 常用命令

| 任务 | 命令 |
|---|---|
| 运行基础 LLM demo | `python -m demos.demo_01__glm_basic` |
| 运行单 Agent 售后 demo | `python -m demos.demo_02_after_sales_agent` |
| 运行多 Agent demo | `python -m demos.demo_03_master_worker` |
| 检查整个 `src` 语法 | `python -m compileall src` |
| 检查单个模块语法 | `python -m compileall src/my_agent/mini_agent.py` |

## 架构说明

### LLM 基础层

`src/llm/base.py` 中的 `BaseLLMCaller` 负责：

| 能力 | 说明 |
|---|---|
| 客户端初始化 | 初始化 `ZhipuAiClient` |
| 消息构造 | 注入基础 `system_prompt`，并在结构化输出时追加额外 system prompt |
| JSON 提取 | 兼容模型返回 ```json 代码块或纯 JSON 文本 |
| 结构化输出 | 将 Pydantic schema 转成 JSON Schema 注入 prompt，再用 `model_validate_json()` 做本地校验 |

### Prompt 工具层

`src/prompts/utils.py` 当前只保留一个公共方法：

| 方法 | 作用 |
|---|---|
| `prompt(text: str) -> str` | 对多行字符串执行 `dedent(...).strip()`，统一清理缩进 |

### Agent 层

`src/my_agent/mini_agent.py` 中的 `MiniAgent` 是一个简化版 ReAct Agent：

1. 根据角色 prompt 和工具描述构造 system prompt
2. 调用模型输出结构化 JSON
3. 解析为 `tool_call` 或 `final_answer`
4. 执行工具
5. 将 `Observation` 追加回消息历史，继续下一轮

工具描述来自工具函数本身的：

| 来源 | 影响 |
|---|---|
| docstring | 直接进入模型可见的工具说明 |
| Python 函数签名 | 决定模型看到的参数名与参数结构 |

修改工具签名或 docstring，会直接影响模型的工具调用行为。

### 多 Agent 编排层

`src/my_agent/multi_agent_orchestrator.py` 中的 `MultiAgentOrchestrator` 负责：

1. 先把用户请求拆成 `TaskPlan`
2. 根据 `worker_type` 分发给不同 `MiniAgent`
3. 汇总各专家结果
4. 再调用一次模型生成最终答复

这是一个典型的 master-worker 模式示例。

## 仓库约定

### Prompt 约定

所有**多行 prompt** 一律使用 `src/prompts/utils.py` 中的 `prompt()` 处理。

示例：

```python
from src.prompts import prompt

system_prompt = prompt("""
    你是一个售后助手。
    你需要帮助用户完成退货流程。
""")
```

约定如下：

| 规则 | 要求 |
|---|---|
| 多行 prompt | 必须使用 `from src.prompts import prompt` 包裹 |
| `src/prompts/utils.py` | 暂时只放通用文本处理方法，不放业务 prompt builder |
| 直接三引号多行字符串 | 不要裸用缩进版本，避免空格污染实际 prompt 内容 |

### 导入约定

仓库内部统一使用 `src...` 形式导入。

| 推荐 | 不推荐 |
|---|---|
| `from src.llm.base import BaseLLMCaller` | `from llm.base import BaseLLMCaller` |
| `from src.prompts import prompt` | `from prompts import prompt` |

### 结构化输出约定

所有基于 Pydantic 的结构化输出，统一走 `BaseLLMCaller.call_llm_with_pydantic()`，不要在业务代码里手动拼 JSON Schema 或自行解析 JSON。

## 验证方式

当前仓库没有现成的测试框架、pytest 配置或 lint 配置。

修改后优先这样验证：

| 顺序 | 操作 |
|---|---|
| 1 | `python -m compileall src` |
| 2 | 运行相关 demo |
| 3 | 检查结构化输出链路是否仍能正常工作 |

## 备注

`demos/` 中的数据和工具大多是 mock 数据，主要用于演示 Agent 编排与工具调用流程，不代表真实业务接入方式。