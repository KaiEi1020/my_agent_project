import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.my_agent.mini_agent import MiniAgent
from src.prompts import prompt
from src.tools.mock_tools import (
    check_refund_policy,
    get_order_details,
    get_user_info,
    get_user_orders,
    initiate_refund,
)


load_dotenv()


def run_demo():
    """测试智能售后 Agent"""
    system_prompt = prompt("""
        你是一个专业的电商售后客服助手。
        你的目标是协助用户处理退货申请，并始终保持专业、高效且符合公司政策。
    """)

    tools = {
        "get_user_orders": get_user_orders,
        "get_order_details": get_order_details,
        "initiate_refund": initiate_refund,
        "check_refund_policy": check_refund_policy,
        "get_user_info": get_user_info,
    }

    agent = MiniAgent(system_prompt=system_prompt, tools=tools)

    print("=" * 60)
    print("智能售后 Agent 启动")
    print("=" * 60)

    user_input = "我想退货，上周买的 iPhone"
    print(f"\n[用户]: {user_input}\n")

    result = agent.run(user_input)
    print(f"\n[最终结果]: {result}")


if __name__ == "__main__":
    run_demo()
