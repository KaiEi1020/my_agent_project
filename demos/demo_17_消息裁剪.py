# ==========================================
# 🚨 1.X 标准工业模板：固化 load_dotenv()
# ==========================================
from dotenv import load_dotenv
import os
load_dotenv() 

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, trim_messages
from langgraph.graph import StateGraph, START, END

# 初始化智谱大脑
model = ChatOpenAI(
    model=os.getenv("ZAI_MODEL"),
    openai_api_key=os.getenv("ZAI_API_KEY"),
    openai_api_base="https://open.bigmodel.cn/api/paas/v4/",
    temperature=0, 
)

# ==========================================
# 🛠️ 核心：在节点内部配置 1.x 标准消息裁剪器
# ==========================================
# trim_messages 可以根据消息数量（max_tuples）或 Token 数进行精准裁剪
message_trimmer = trim_messages(
    max_tuples=5,                 # 严格限制：进发给大模型的上下文最多只能带 5 条消息
    strategy="last",              # 策略：保留最新的消息
    token_counter=len,            # 简单计数器（生产环境可用智谱专用的 Token 计算器）
    include_system=True,          # 铁律：无论怎么裁剪，最顶部的 SystemMessage（红线提示词）绝对不能删
    start_on="human",             # 裁剪后的第一条消息必须是用户发的，确保语义连贯
)

# 模拟定义状态
class SlimState(dict):
    messages: list
    transfer_amount: int

# 重构后的大脑节点：具备自我成本防御能力
def defensive_brain_node(state: SlimState):
    print(f"📊 [裁剪前] 检查点中的原始历史消息总数: {len(state['messages'])}")
    
    # 🚨 临门一脚：在送入 Stateless 大模型前，执行强行瘦身
    trimmed_history = message_trimmer.invoke(state["messages"])
    
    print(f"✂️ [裁剪后] 真正喂给智谱模型的瘦身消息总数: {len(trimmed_history)}")
    
    # 将瘦身后的干净数据集送入大模型，拒绝为历史废话买单
    response = model.invoke(trimmed_history)
    
    amount = 1000 if "1,000" in response.content else 100000
    return {"messages": [response], "transfer_amount": amount}