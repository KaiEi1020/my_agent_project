import typing
from typing import Annotated, Literal, TypedDict
import operator
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import asyncio

# ==========================================
# 1. 状态工程 (State) - 使用 Dict 局部覆盖设计
# ==========================================
def merge_reports(old_dict: dict, new_dict: dict) -> dict:
    """自定义 Reducer：实现字典的精准局部 Merge，防止并发覆盖"""
    combined = old_dict.copy() if old_dict else {}
    combined.update(new_dict)
    return combined

class PipelineState(TypedDict):
    code_content: str                                      # 待审计的核心代码
    audit_reports: Annotated[dict, merge_reports]         # 并行 Agent 回传的报告字典
    next_node: str                                         # 路由控制变量
    deployment_approved: bool                              # 人类审批状态

# ==========================================
# 2. 节点定义 (Nodes)
# ==========================================

# 2.1 Supervisor 主管节点
def supervisor_node(state: PipelineState):
    print("\n[Node: 🤖 Supervisor] 研判流水线状态...")
    reports = state.get("audit_reports", {})

    # 策略 1：如果还没有审计报告，启动 Map-Reduce 并行分发
    if not reports:
        print("   -> 触发 Map-Reduce：下发任务给安全和性能智能体。")
        return {"next_node": "PARALLEL_AUDIT"}

    # 策略 2：如果两个并行审计都完了，准备进入人类审批环节
    if "security" in reports and "performance" in reports:
        # 如果已经被人类修改并批准
        if state.get("deployment_approved"):
            print("   -> 人类已批准！进入最终部署节点。")
            return {"next_node": "deploy_node"}
        else:
            print("   -> 审计完毕。准备拦截流，移交人类总监审批。")
            return {"next_node": "human_approval_gate"}

# 2.2 审计分发器：负责触发并行审计
def audit_dispatcher(state: PipelineState):
    """空节点，仅作为并行分发的锚点"""
    print("\n[Node: 📡 Audit Dispatcher] 分发并行审计任务...")
    return {}

# 2.3 Worker 1: 安全审计智能体 (Map 分支 A)
def security_agent(state: PipelineState):
    print("\n[Node: 🛡️ Security Agent] 正在扫描代码漏洞...")
    # 模拟安全检查
    return {"audit_reports": {"security": "PASSED - 未发现 SQL 注入风险。"}}

# 2.4 Worker 2: 性能审计智能体 (Map 分支 B)
def performance_agent(state: PipelineState):
    print("\n[Node: ⚡ Performance Agent] 正在分析时间复杂度...")
    # 模拟发现一个潜在的性能死循环问题
    return {"audit_reports": {"performance": "WARNING - 发现潜在的死循环风险！建议修改。"}}

# 2.5 Human Gate: 人类审批闸门（空节点，仅作为中断锚点）
def human_approval_gate(state: PipelineState):
    # 这个节点不写逻辑，纯粹用来作为流程被挂起时的标记节点
    return {"next_node": "supervisor"}

# 2.6 最终执行节点: 部署上线
def deploy_node(state: PipelineState):
    print(f"\n[Node: 🚀 部署系统] 正在发布最终代码：\n{state['code_content']}")
    print("✨ [系统通知] 代码发布成功！流水线完美闭环。")
    return {}

# ==========================================
# 3. 图拓扑编排 (Graph Topology)
# ==========================================
workflow = StateGraph(PipelineState)

# 注册所有节点
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("audit_dispatcher", audit_dispatcher)
workflow.add_node("security_agent", security_agent)
workflow.add_node("performance_agent", performance_agent)
workflow.add_node("human_approval_gate", human_approval_gate)
workflow.add_node("deploy_node", deploy_node)

# 编排边界
workflow.add_edge(START, "supervisor")

# 从 Supervisor 出来的动态条件路由
workflow.add_conditional_edges(
    "supervisor",
    lambda state: state["next_node"],
    {
        "PARALLEL_AUDIT": "audit_dispatcher",
        "human_approval_gate": "human_approval_gate",
        "deploy_node": "deploy_node",
    }
)

# 分发器并行触发两个审计 Agent（LangGraph 中一个节点的多条出边会并行执行）
workflow.add_edge("audit_dispatcher", "security_agent")
workflow.add_edge("audit_dispatcher", "performance_agent")

# 并行节点执行完后，重新汇聚 (Reduce) 到 Supervisor
workflow.add_edge("security_agent", "supervisor")
workflow.add_edge("performance_agent", "supervisor")
workflow.add_edge("human_approval_gate", "supervisor")
workflow.add_edge("deploy_node", END)

# 💡 核心：编译图，并配置在人类审批闸门节点之前强行中断！
memory = MemorySaver()
app = workflow.compile(checkpointer=memory, interrupt_before=["human_approval_gate"])


async def run_pipeline():
    # 给定一个包含 Bug 的初始代码
    initial_input = {
        "code_content": "while True: print('Running...') # 危险代码",
        "audit_reports": {},
        "deployment_approved": False
    }
    config = {"configurable": {"thread_id": "prod_release_026"}}

    print("=== 🎬 第一阶段：流水线启动，Agent 兵团自动协同 ===")
    # 触发流式传输
    async for event in app.astream(initial_input, config, stream_mode="updates"):
        print(f"📡 [流式快讯] 节点集合 {list(event.keys())} 执行完毕")

    # -------------------------------------------------------------
    # 🛑 此时，流水线必定一头撞在 human_approval_gate 前面，强制暂停
    # -------------------------------------------------------------
    print("\n==================================================")
    print("🛑 警报：流水线已触发安全熔断！进入人类架构师审批视图。")
    current_state = await app.aget_state(config)
    print(f"👉 当前挂起位置: {current_state.next}")
    print(f"📊 当前收集到的审计报告: {current_state.values['audit_reports']}")
    print("==================================================\n")

    print("=== 🛠️ 第二阶段：人类介入，显式状态修改 (State Mutation) ===")
    # 人类发现性能有警告，决定手动把代码修复掉，并更改审批状态为 True！
    fixed_state = {
        "code_content": "for i in range(10): print('Running safely...') # 人类修复版",
        "deployment_approved": True
    }

    print("✍️ 人类总监正在后台重写危险代码，并签署批准令牌...")
    await app.aupdate_state(config, fixed_state, as_node="human_approval_gate")

    print("\n=== 🚀 第三阶段：恢复运行，流水线带着修正后的状态冲向终点 ===")
    # 传入 None 告诉 LangGraph 从上一次中断的检查点直接苏醒并继续跑
    async for event in app.astream(None, config, stream_mode="updates"):
        print(f"📡 [流式快讯] 节点集合 {list(event.keys())} 执行完毕")

# 运行异步流水线
if __name__ == "__main__":
    asyncio.run(run_pipeline())
