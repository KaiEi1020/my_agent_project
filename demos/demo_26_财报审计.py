from typing import TypedDict, List, Dict, Annotated
import operator
from langgraph.graph import StateGraph, START, END

# ==========================================
# 1. 状态工程 (State)
# ==========================================
def append_audit_logs(old_logs: List[str], new_logs: List[str]) -> List[str]:
    return (old_logs or []) + new_logs

class MultiModalAuditState(TypedDict):
    chart_image_urls: List[str]                 # S3 图片指针 URL
    raw_financial_data: Dict[str, float]        # 原始财务数据字典
    vision_analysis_revenue: float              # 🖼️ Vision 节点看到的营收数字
    code_calculated_revenue: float              # 🐍 Code 节点用 Pandas 算出的营收数字
    is_verified: bool                           # ⚖️ 交叉验证状态
    loop_count: int                             # 避坑防御：防死循环计数器
    audit_logs: Annotated[List[str], append_audit_logs]

# ==========================================
# 2. 节点定义 (Nodes)
# ==========================================

def vision_agent(state: MultiModalAuditState):
    """模拟多模态视觉节点"""
    logs = []
    current_loop = state.get("loop_count", 0)
    
    print("\n[Node: 🖼️ Vision Agent] 正在通过视觉解析财报折线图...")
    print(f"   -> 正在读取 S3 资产指针: {state['chart_image_urls']}")
    
    # 模拟大模型视觉幻觉：第一次看图时，把 1500 万看成了 1300 万 (数错了)
    if current_loop == 0:
        detected_revenue = 1300.0
        logs.append("【Vision 审计】看图得出 Q3 营收大约为 1300 万（产生视觉幻觉）。")
    else:
        # 第二次重审时，模型“擦亮双眼”，看出了正确答案 1500 万
        detected_revenue = 1500.0
        logs.append("【Vision 审计】重审图表，校正 Q3 营收为 1500 万。")
        
    return {
        "vision_analysis_revenue": detected_revenue,
        "audit_logs": logs,
        "loop_count": current_loop + 1
    }

def code_evaluator(state: MultiModalAuditState):
    """模拟 E2B 代码沙箱节点"""
    print("\n[Node: 🐍 Code Evaluator] 启动 E2B 沙箱，运行 Python/Pandas 计算原始数据...")
    
    # 模拟在沙箱中执行：df['revenue'].sum()，得出绝对精确的真理值 1500 万
    raw_data = state["raw_financial_data"]
    precise_revenue = raw_data.get("q3_revenue", 0.0)
    
    return {
        "code_calculated_revenue": precise_revenue,
        "audit_logs": [f"【沙箱计算】Pandas 运行完成，得出真理值：{precise_revenue} 万。"]
    }

def cross_checker(state: MultiModalAuditState):
    """交叉比对验证节点"""
    print("\n[Node: ⚖️ Cross-Checker] 开始双向数据对齐验证...")
    v_rev = state["vision_analysis_revenue"]
    c_rev = state["code_calculated_revenue"]
    
    # 比对两者差距
    if abs(v_rev - c_rev) < 0.01:
        print("   ✅ 验证通过：视觉推断与代码计算完全对齐！")
        return {
            "is_verified": True,
            "audit_logs": ["【交叉验证】双向数据完全一致，审计合规，准予发布！"]
        }
    else:
        print(f"   ❌ 警报：视觉数值 ({v_rev}万) 与沙箱数值 ({c_rev}万) 发生冲突！")
        return {
            "is_verified": False,
            "audit_logs": [f"【交叉验证】数据冲突（视觉:{v_rev} vs 沙箱:{c_rev}），拒绝放行，打回重审！"]
        }

# ==========================================
# 3. 动态路由与拓扑编排 (Topology)
# ==========================================
def router_decision(state: MultiModalAuditState):
    """决定是放行还是打回"""
    if state["is_verified"]:
        return "approved_end"
    
    # 防御性编程：如果重试了 3 次还不对，强制报错熔断，防止无限死循环
    if state["loop_count"] >= 3:
        print("🚨 [安全熔断] 连续重审失败，可能存在恶意图片干扰，强制中断！")
        return "force_end"
        
    return "reject_retry"


# 构筑图结构
workflow = StateGraph(MultiModalAuditState)

# 注册节点
workflow.add_node("vision_agent", vision_agent)
workflow.add_node("code_evaluator", code_evaluator)
workflow.add_node("cross_checker", cross_checker)

# 连线：START 之后，Vision 和 Code 同时并发跑（Map 拓扑）
workflow.add_edge(START, "vision_agent")
workflow.add_edge(START, "code_evaluator")

# 并发节点汇聚到 Cross-Checker (Reduce 拓扑)
workflow.add_edge("vision_agent", "cross_checker")
workflow.add_edge("code_evaluator", "cross_checker")

# 从 Cross-Checker 出来的动态条件路由
workflow.add_conditional_edges(
    "cross_checker",
    router_decision,
    {
        "approved_end": END,                 # 验证通过，圆满结束
        "force_end": END,                    # 熔断报错，强制结束
        "reject_retry": "vision_agent"       # 验证失败，单向打回给 Vision 重新看图！
    }
)

app = workflow.compile()


if __name__ == "__main__":
    # 模拟初始输入
    initial_input = {
        "chart_image_urls": ["s3://company-vault/2026/q3_report_chart.png"],
        "raw_financial_data": {"q3_revenue": 1500.0}, # 真理值是 1500 万
        "loop_count": 0,
        "is_verified": False,
        "audit_logs": []
    }
    
    print("=== 🎬 启动企业多模态资产审计流水线 ===")
    config = {"configurable": {"thread_id": "audit_task_999"}}
    
    # 运行图并打印最终状态
    final_state = app.invoke(initial_input, config)
    
    print("\n==================================================")
    print("📜 最终全链路追溯日志（Audit Trail Logs）：")
    for idx, log in enumerate(final_state["audit_logs"], 1):
        print(f"{idx}. {log}")
    print("==================================================")