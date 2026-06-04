import os
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage


load_dotenv()

# 1. 定义一个极其严谨的工具（带完美注释）
@tool
def calculate_refund_amount(days_passed: int, original_price: float) -> float:
    """根据购买天数计算应退金额。
    
    Args:
        days_passed: 距离购买之日已经过去的天数。
        original_price: 商品购买时的原始价格。
    """
    if days_passed <= 7:
        return original_price # 7天内全额退款
    elif days_passed <= 30:
        return original_price * 0.8 # 30天内折旧退 80%
    return 0.0 # 超过30天不予退款

# 2. 初始化模型并死死绑定这个工具
model = ChatOpenAI(
    model=os.getenv("ZAI_MODEL"),
    openai_api_key=os.getenv("ZAI_API_KEY"),
    temperature=0,
    openai_api_base="https://open.bigmodel.cn/api/paas/v4/"
)
model_with_tools = model.bind_tools([calculate_refund_amount])


# 1. 模拟第一轮：用户的提问
user_msg = HumanMessage(content="我10天前买了一件 500 块钱的衣服，现在想退，能退多少钱？")

# 2. 模拟大模型的返回：它决定调工具，并生成了一个叫 'call_abc123' 的 ID
ai_msg = AIMessage(
    content="", 
    tool_calls=[{
        'name': 'calculate_refund_amount', 
        'args': {'days_passed': 10, 'original_price': 500}, 
        'id': 'call_abc123' # <--- 记住这个ID
    }]
)

# 3. 程序员在后台用 Python 算出了结果：400.0
# 我们必须用 ToolMessage 包装这个结果，并死死绑定刚才的 ID！
tool_msg = ToolMessage(
    content="400.0",                 # 工具执行的真实结果
    tool_call_id="call_abc123"       # 完美的对齐你说的 id！
)

# 4. 把这三条历史记录打包，再次丢给大模型（让它知道前因后果）
chat_history = [user_msg, ai_msg, tool_msg]

# 再次调用模型（此时它看到了工具结果，就不会再调工具了，而是转入“总结陈词”）
final_reply = model_with_tools.invoke(chat_history)

print("==== 大模型的最终人话 ====")
print(final_reply.content)