import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.my_agent.mini_agent import MiniAgent
from src.my_agent.multi_agent_orchestrator import MultiAgentOrchestrator
from src.prompts import prompt
from src.tools.mock_tools import (
    book_flight,
    check_refund_policy,
    get_order_details,
    get_user_info,
    get_user_orders,
    initiate_refund,
    search_flights,
)


load_dotenv()


def build_refund_agent() -> MiniAgent:
    system_prompt = prompt("""
        你是一个专业的电商售后专家。
        你的职责是帮助用户定位订单、校验退货条件，并在符合政策时发起退货。
        如果信息足够，就直接完成退货，不要把本来可以代办的事情推回给用户。
    """)

    tools = {
        "get_user_info": get_user_info,
        "get_user_orders": get_user_orders,
        "get_order_details": get_order_details,
        "check_refund_policy": check_refund_policy,
        "initiate_refund": initiate_refund,
    }
    return MiniAgent(system_prompt=system_prompt, tools=tools)


def build_travel_agent() -> MiniAgent:
    system_prompt = prompt("""
        你是一个机票与行程助手。
        你的职责是查询下周去上海的机票，并根据天气决定是否订票。
        规则：
        1. 必须先查询航班信息。
        2. 只有天气是“晴”时，才能调用订票工具。
        3. 如果有多个晴天航班，优先选择价格最低的一班。
        4. 如果没有晴天航班，明确告诉用户暂未订票。
    """)

    tools = {
        "get_user_info": get_user_info,
        "search_flights": search_flights,
        "book_flight": book_flight,
    }
    return MiniAgent(system_prompt=system_prompt, tools=tools)


def run_demo():
    orchestrator = MultiAgentOrchestrator(
        workers={
            "REFUND": build_refund_agent(),
            "TRAVEL": build_travel_agent(),
        }
    )

    user_input = "帮我把上周购买的红色衬衫退了，顺便帮我查查下周去上海的机票，只要晴天就帮我订一张。"

    print("=" * 60)
    print("Master-Worker 多 Agent Demo 启动")
    print("=" * 60)
    print(f"\n[用户]: {user_input}\n")

    result = orchestrator.dispatch(user_input)
    print(f"\n[最终结果]: {result}")


if __name__ == "__main__":
    run_demo()
