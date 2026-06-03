# Agent是什么

## Workflow和Agent核心区别

*   Workflow 是硬编码的顺序执行，而 Agent 的核心在于动态推理
*   AI Agent (智能体) 对比 Workflow Automation (工作流自动化)，最大区别是拥有**感知 (Perception) 和推理 (Reasoning) 能力。**



## Agent Loop（智能体循环）

1. 最经典：Think → Act → Observe
2. Perception (感知)→ Planning (规划) → Action (行动)→Observation 
   1. 后来大家发现think太笼统， Think=Perception+Planning
3. State → Planning → Action → Observation → Reflection
   1. 这是现代 Agent Framework 更接近的架构
   2. State: 我是谁？我在做什么？做到哪一步了？还剩什么没做？
   3. State=Input+History+Memory+Environment
      1. 当前目录
      2. Git状态
      3. 已修改文件
      4. 运行结果
      5. 错误日志
   4. Planning
      1. 静态规划：先一次拆完
      2. 动态规划：每完成一步重新规划
   5. Observation: 工具返回的结果。（是事实）
   6. Reflection：（是解释，本质是一个 Review）
      1. 刚才发生了什么？意味着什么？下一步计划要不要变？
      2. 观察结果
         ↓
         评价结果
         ↓
         决定是否调整



现代agent更像：

```
State
↓
Perception
↓
Planning
↓
Action
↓
Observation
↓
Evaluation (Reflection)
↓
Replan ?
↓
Update State
↓
Next Loop
```



从工程视角看，Reflection 最接近：

```ts
function reflect(observation) {
  return {
    success: boolean,
    confidence: number,
    errorReason: string,
    needReplan: boolean
  }
}
```

# Python 基础

虚拟环境

```bash
python3 -m venv venv

source venv/bin/activate
```

- 使用 Python 3 的 venv 模块创建一个虚拟环境
- 第二个 venv 是虚拟环境的目录名称
- source 会读取文件中的命令，并在当前 shell 进程中直接执行
- 激活刚创建的虚拟环境
- 激活后，所有的 Python 和 pip 命令都会使用这个虚拟环境中的版本



# RAG（检索增强）

# 参数调优

## 1. 温度 (Temperature)

*   **Temp = 0：** 模型会永远选择概率最高的那一个 Token。**（确定性最强）**

    *   *适用场景：* 提取 JSON 字段、写代码、数学计算。
*   **Temp = 0.7 - 1.0：** 概率分布被平滑，模型开始尝试一些“非最优”但“有新意”的选项。

    *   *适用场景：* 创意写作、聊天机器人。

==在构建 Tool Use（工具调用） 型 Agent 时，通常将温度设为 0，以防止模型在生成 API 参数时“自由发挥”。==

## 2. Top-p (核采样)

与温度不同，Top-p 像是一个\*\*“备选过滤器”\*\*。

*   如果 `top_p = 0.1`，模型只会在累积概率达到前 10% 的 Token 中选择。
*   这能有效剔除那些概率极低、胡言乱语的“长尾”选项。

## 3. 停止序列 (Stop Sequences)

# 结构化推理引导 (Structured Reasoning)

专家级“退货 Agent” System Prompt 示例

```markdown
## Role
你是一个专业的电商售后退货专家。你的目标是协助用户处理退货申请，并始终保持专业、高效且符合公司政策。

## Capabilities (Tools)
你必须通过以下工具获取信息或执行操作，严禁编造数据：
1. `get_user_orders(user_id, timeframe)`：查询用户在特定时间范围内的订单列表。
2. `get_order_details(order_id)`：获取特定订单的详细信息（如商品、购买日期、状态）。
3. `initiate_refund(order_id, reason)`：正式发起退货流程。

## Workflow (ReAct Protocol)
对于每个任务，你必须遵循以下严格的思考路径：
- Thought: 分析当前已知信息，判断下一步需要做什么（感知与规划）。
- Action: 调用上述工具之一。格式为：工具名(参数)。
- Observation: (系统将返回工具执行结果)。
- Reflection: 评估 Observation 的内容。如果信息不足则继续规划；如果达成目标则输出 Final Answer；如果遇到错误或不符合退货政策，需思考替代方案。

## Policies & Constraints
1. 仅限处理“上周”的订单（今天是 2026-04-26）。
2. 如果用户要求退回的商品不在订单列表中，需礼貌询问。
3. 如果退货条件不满足（如超过期限），需解释原因并尝试引导至人工客服。
4. 严禁在没有获得 Observation 之前给出 Final Answer。m
```

# 最大循环限制 (Max Loops) 与 终止条件 (Termination)

1.  为什么会发生“无限循环”？
    *   幻觉纠缠： 模型认为它调用了工具，但 Observation 返回错误，它不反思而是不停重试同样的错误动作。
    *   乒乓效应： 工具 A 的输出让模型想调用工具 B，工具 B 的输出又让它想调用 A。
2.  专家级的“三重防护”&#x20;
    *   次数锁 (Max Iterations)： 强制规定一个 Agent 为了解决一个问题，最多只能跑 5 轮或 10 轮。超过这个次数，直接人工接入。
    *   Token 锁 (Max Tokens)： 限制单次任务的总消耗，防止模型输出极长的废话。
    *   语义终点 (Finish Reason)： 只有当模型输出包含特定的关键词（如 ==Final Answer:==）时，循环才正式结束。
3.  工具调用的“幂等性” (Idempotency)
    这是工程化中的高级概念。你==要确保 Agent 如果重复调用了同一个“扣费”或“发邮件”工具，系统不会真的扣两次费或发两封邮件==。



# 成本

#### 专家策略：模型路由 (Model Routing)

**简单任务（如分类、格式化）：** 路由给低成本的小模型（如 GPT-4o-mini 或 7B 级别的开源模型）

**核心逻辑（如任务拆解、多步推理）：** 路由给高智能的大模型（如 GPT-4o 或 Claude 3.5 Sonnet）





# 动态Few-Shot (Dynamic Few-Shot Injection)

动态 Few-Shot