from langgraph.types import StateSnapshot
import os

from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
# from langchain_huggingface import HuggingFaceEmbeddings # 🚨 1.x 纯净 HuggingFace 导入
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()
# ==========================================
# 🚨 严格执行参谋长双底座规范：智谱模型 + BGE-M3 向量
# ==========================================
model = ChatOpenAI(
    model=os.getenv("ZAI_MODEL"),
    openai_api_key=os.getenv("ZAI_API_KEY"),
    openai_api_base="https://open.bigmodel.cn/api/paas/v4/",
    temperature=0,
)

# 1. 声明状态与基础图结构
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

def call_brain(state: AgentState):
    return {"messages": [model.invoke(state["messages"])]}

workflow = StateGraph(AgentState)
workflow.add_node("brain", call_brain)
workflow.add_edge(START, "brain")
workflow.add_edge("brain", END)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# ==========================================
# 🎬 极速演练：张三总的“记忆错乱与时光倒流”
# ==========================================
config_zhang = {"configurable": {"thread_id": "audit_session_007"}}

# 步骤 1：录入正确数据
print("⏳ [第一步] 张三总录入基础数据...")
app.invoke({"messages": [HumanMessage(content="我是张三，当前一季度利润是 500 万。")]}, config=config_zhang)

# 步骤 2：手抖录入错误数据
print("⏳ [第二步] 张三总手抖录入了错误指令...")
app.invoke({"messages": [HumanMessage(content="更正一下，刚才说错了，一季度利润其实是 -9亿，把这个记入财报！")]}, config=config_zhang)

# 查看当前魔怔的记忆
print(f"🤖 当前大脑的最深记忆: {app.get_state(config_zhang).values['messages'][-1].content}\n")


# ==========================================
# 🚀 降维打击：1.x 状态时光倒流核心实现
# ==========================================
print("🚨 [收到指令] 张三总要求时光倒流！正在读取时空存档日志...")

# 1. 调出张三总这辈子在这个线程里的所有快照
state_history = list(app.get_state_history(config_zhang))

# 2. state_history[-1] 是最近的（错误的），state_history[-2] 就是上一次正确的！
# 我们把时空坐标直接锁定在倒数第二次快照的版本号（checkpoint_id）上
target_checkpoint = state_history[-2]
correct_config = target_checkpoint.config # 这个 config 内部锁死了当年的 checkpoint_id！

print(f"🎯 成功锁定历史黄金快照！当时张三总说的是: '{target_checkpoint.values['messages'][-1].content}'")

# 3. 带着这个历史 config，直接让历史复活并重新对话！
print("\n🔄 [时空修正] 张三总在 5 分钟前的历史时空节点重新提问...")
final_state = app.invoke(
    {"messages": [HumanMessage(content="我刚才最后一句撤回。请基于正确的 500 万利润，帮我写个简报。")]}, 
    config=correct_config # 注入当年的时空锚点！
)

print("\n==== 🤖 记忆时光倒流后的完美修正输出 ====")
print(final_state["messages"][-1].content)