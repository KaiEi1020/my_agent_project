# ==========================================
# 🚨 固化标准：第一行雷打不动自动加载环境变量
# ==========================================
from dotenv import load_dotenv
load_dotenv() 

import os
from typing import Annotated
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

# 🚨 严格执行参谋长双底座初始化规范
model = ChatOpenAI(
    model=os.getenv("ZAI_MODEL"),
    openai_api_key=os.getenv("ZAI_API_KEY"),
    openai_api_base="https://open.bigmodel.cn/api/paas/v4/",
    temperature=0,
)

# 1. 定义图状态：包含我们要审计打款的金额
class AuditState(TypedDict):
    messages: Annotated[list, add_messages]
    transfer_amount: int # 核心业务数据：打款金额

# 节点 A：大脑决策节点
def auditor_brain(state: AuditState):
    print("🤖 [大脑节点] 收到审计请求，正在计算最终打款金额...")
    # 模拟大模型发生幻觉，把 1000 元算成了 100000 元！
    return {
        "messages": [HumanMessage(content="审计完毕，判定应打款 100,000 元。")],
        "transfer_amount": 100000
    }

# 节点 B：高危执行节点（网银出账）
def execute_bank_transfer(state: AuditState):
    print(f"💰 [网银出账节点] 🔥 危险行动！！！正向账户打款 {state['transfer_amount']} 元！")
    print("✅ [网银出账节点] 打款成功，自动生成电子回单。")
    return {"messages": [HumanMessage(content="系统已自动完成线上打款。")]}

# 2. 组装 1.x 拓扑图
workflow = StateGraph(AuditState)
workflow.add_node("auditor_brain", auditor_brain)
workflow.add_node("execute_bank_transfer", execute_bank_transfer)

workflow.add_edge(START, "auditor_brain")
workflow.add_edge("auditor_brain", "execute_bank_transfer")
workflow.add_edge("execute_bank_transfer", END)

# 3. 记忆胶囊挂载
memory = MemorySaver()

# ==========================================
# 🚨 核心：在执行高危转账节点前，强行设置断点拦截！
# ==========================================
app = workflow.compile(
    checkpointer=memory,
    interrupt_before=["execute_bank_transfer"] # 在进发网银前，时空拉闸！
)

# 4. 模拟运行
config_thread = {"configurable": {"thread_id": "high_risk_transfer_001"}}

print("🚀 [系统启动] 初始任务：张三总提交了一张报销发票...")
initial_state = app.invoke(
    {"messages": [HumanMessage(content="请帮我把这张发票审计并打款。")], "transfer_amount": 0}, 
    config=config_thread
)

# ==========================================
# 🛑 见证奇迹：时空冻结
# ==========================================
print("\n⏸️ [时空拉闸] 图流转已瞬间挂起！控制权交还给人类经理。")

# 检查当前被冻结的状态
current_snapshot = app.get_state(config_thread)
print(f"👁️ [人类经理视角] 审阅大脑判定数据...")
print(f"-> 大脑当前决策内容: {current_snapshot.values['messages'][-1].content}")
print(f"-> 大脑准备转账金额: {current_snapshot.values['transfer_amount']} 元")

# 发现金额错误！执行方案 B：人类直接强行干预，重写 State 里的金额
print("\n🛠️ [人类干预] 参谋长发现大模型算错账，强行将转账金额更正为 1000 元！")
app.update_state(
    config_thread,
    {"transfer_amount": 1000}, # 覆写状态！
    # 基于检查点的状态覆写与节点重定向（State Overwrite & Node Redirection）
    as_node="auditor_brain"     # 声明是以 auditor_brain 节点的名义修正的 
)

# ==========================================
# ▶️ 解冻时空：让 Agent 带着人类的正确意志继续跑
# ==========================================
print("\n▶️ [时空解冻] 输入放行信号，让 Agent 带着更正后的参数跑完后续自动化...")
# 传入 None，表示不需要输入新消息，直接顺着断点往下轰油门
final_state = app.invoke(None, config=config_thread)

print("\n==== 🤖 全链路协同演练大圆满完成 ====")