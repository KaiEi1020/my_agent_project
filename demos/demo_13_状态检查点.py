import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver # 🚨 1.x 标准内存检查点

load_dotenv()

# ==========================================
# 🚨 严格执行参谋长的 1.X 智谱平台初始化规范
# ==========================================
model = ChatOpenAI(
    model=os.getenv("ZAI_MODEL"),
    openai_api_key=os.getenv("ZAI_API_KEY"),
    openai_api_base="https://open.bigmodel.cn/api/paas/v4/",
    temperature=0,
)

# 1. 定义 1.x 图状态结构
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # add_messages 让新消息自动追加到历史记录中，而不是覆盖
    messages: Annotated[list, add_messages]

# 2. 定义大模型大脑节点
def call_brain(state: AgentState):
    response = model.invoke(state["messages"])
    return {"messages": [response]}

# 3. 构建图画布
workflow = StateGraph(AgentState)
workflow.add_node("brain", call_brain)
workflow.add_edge(START, "brain")
workflow.add_edge("brain", END)

# ==========================================
# 💾 核心：挂载 1.x 标准状态持久化检查点
# ==========================================
memory_checkpointer = MemorySaver()

# 编译图时，强行把“记忆胶囊”挂载进去
app = workflow.compile(checkpointer=memory_checkpointer)

# ==================== 🎬 第一幕：模拟上周一的对话 ====================
print("📅 [时间：上周一]")

# 声明张总的独一无二的会话线程ID
config_zhang = {"configurable": {"thread_id": "user_session_zhang_007"}}

msg_1 = HumanMessage(content="你好，我是张三。我正在审计公司 2026 年的第一季度财报。")
state_1 = app.invoke({"messages": [msg_1]}, config=config_zhang)
print(f"🤖 Agent 回复: {state_1['messages'][-1].content}\n")


# ==================== 🎬 第二幕：模拟今天，张总再次上线 ====================
print("📅 [时间：今天（用户跨越时空再次上线）]")

# 只要我们带着当年一模一样的 thread_id 重新切入
msg_2 = HumanMessage(content="忙完了。你还记得我是谁吗？我刚才说我在审计什么？")
state_2 = app.invoke({"messages": [msg_2]}, config=config_zhang)

print(f"🎯 传回相同 Thread ID 后，Agent 的记忆复活回复：")
print(state_2["messages"][-1].content)