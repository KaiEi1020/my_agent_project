import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode


load_dotenv()


@tool
def calculate_refund_amount(days_passed: int, original_price: float) -> float:
    """根据购买天数计算应退金额。

    Args:
        days_passed: 距离购买之日已经过去的天数。
        original_price: 商品购买时的原始价格。
    """
    if days_passed <= 7:
        return original_price  # 7天内全额退款
    if days_passed <= 30:
        return original_price * 0.8  # 30天内折旧退 80%
    return 0.0  # 超过30天不予退款


model = ChatOpenAI(
    model=os.getenv("ZAI_MODEL"),
    openai_api_key=os.getenv("ZAI_API_KEY"),
    temperature=0,
    openai_api_base="https://open.bigmodel.cn/api/paas/v4/",
)
model_with_tools = model.bind_tools([calculate_refund_amount])


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


def llm_brain(state: AgentState) -> AgentState:
    reply = model_with_tools.invoke(state["messages"])
    return {"messages": [reply]}


def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tool_runner"
    return END


workflow = StateGraph(AgentState)
workflow.add_node("llm_brain", llm_brain)
workflow.add_node("tool_runner", ToolNode(tools=[calculate_refund_amount]))
workflow.add_edge(START, "llm_brain")
workflow.add_conditional_edges("llm_brain", should_continue)
workflow.add_edge("tool_runner", "llm_brain")

app = workflow.compile()


if __name__ == "__main__":
    # 声明安全配置：限制整张图最多只能流转 10 步
    config = {
        "configurable": {"thread_id": "user_session_001"}, # 顺便带上线程ID（用于记忆）
        "recursion_limit": 10  # 限制 llm_brain + tool_runner 总调用次数
    }
    result = app.invoke(
        {
            "messages": [
                HumanMessage(
                    content="我10天前买了一件 500 块钱的衣服，现在想退，能退多少钱？"
                )
            ]
        },
        config=config,
    )

    print("==== 大模型的最终人话 ====")
    print(result["messages"][-1].content)
