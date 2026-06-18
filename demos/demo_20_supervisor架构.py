from typing import Literal, TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

# ==========================================
# 1. 定义全局状态 (State) - 贯彻状态隔离与确定性
# ==========================================
class AgentState(TypedDict):
    messages: list[BaseMessage]
    next_worker: str  # 由 Supervisor 决定下一个去哪

# ==========================================
# 2. 定义打工人节点 (Worker Nodes)
# ==========================================
def coder_agent(state: AgentState):
    print("\n[Node: Coder] 正在疯狂敲代码...")
    new_message = AIMessage(content="【代码已生成】：print('Hello World')")
    return {"messages": [new_message], "next_worker": "supervisor"}

def tester_agent(state: AgentState):
    print("\n[Node: Tester] 正在编写测试用例...")
    new_message = AIMessage(content="【测试用例已生成】：assert output == 'Hello World'")
    return {"messages": [new_message], "next_worker": "supervisor"}

# ==========================================
# 3. 定义主管节点 (Supervisor Node)
# ==========================================
def supervisor_agent(state: AgentState):
    print("\n[Node: Supervisor] 正在研判下一步走向...")
    last_message = state["messages"][-1].content
    
    # 💡 确定性控制逻辑：2026年生产环境常在 Supervisor 内部结合 LLM 结构化输出或硬编码规则
    if "写个代码" in last_message:
        return {"next_worker": "coder_agent"}
    elif "代码已生成" in last_message:
        return {"next_worker": "tester_agent"}
    else:
        return {"next_worker": "FINISH"}

# ==========================================
# 4. 编排状态图 (State Graph)
# ==========================================
workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("supervisor", supervisor_agent)
workflow.add_node("coder_agent", coder_agent)
workflow.add_node("tester_agent", tester_agent)

# 设置入口
workflow.add_edge(START, "supervisor")

# 💡 动态条件路由：根据 supervisor 返回的 next_worker 决定分发到哪
workflow.add_conditional_edges(
    "supervisor",
    lambda state: state["next_worker"],
    {
        "coder_agent": "coder_agent",
        "tester_agent": "tester_agent",
        "FINISH": END
    }
)

# 员工做完事，必须回传给主管
workflow.add_edge("coder_agent", "supervisor")
workflow.add_edge("tester_agent", "supervisor")

# 编译图
app = workflow.compile()


# 模拟用户输入
inputs = {"messages": [HumanMessage(content="请帮我写个代码并做好测试")]}

# 实时流式打印节点更新
print("--- 开始流式执行多智能体网络 ---", flush=True)
for output in app.stream(inputs, stream_mode="updates"):
    print(f"[debug] raw output: {output}", flush=True)
    for node_name, node_output in output.items():
        print(f"📡 [流式通知] 节点 '{node_name}' 执行完毕!", flush=True)
        if "messages" in node_output:
            print(f"      产出内容: {node_output['messages'][-1].content}", flush=True)
print("--- 任务处理完成 ---", flush=True)