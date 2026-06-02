import requests
import zai
import os
from zai import ZhipuAiClient
from dotenv import load_dotenv
from mini_agent import MiniAgent


load_dotenv()  # 加载 .env 文件

# ========== 伪代码工具函数（学习用） ==========

def get_user_orders(user_id: str, timeframe: str = "last_week") -> str:
    """
    查询用户在指定时间范围内的订单列表
    
    Args:
        user_id: 用户 ID
        timeframe: 时间范围，如 "last_week", "last_month"
    
    Returns:
        订单列表的 JSON 字符串
    """
    # 伪代码：实际项目中这里会调用数据库或订单 API
    print(f"[工具调用] get_user_orders(user_id={user_id}, timeframe={timeframe})")
    
    # 模拟返回数据
    orders = [
        {"order_id": "ORD001", "product": "iPhone 15", "price": 7999, "status": "已签收", "date": "2026-05-20"},
        {"order_id": "ORD002", "product": "AirPods Pro", "price": 1899, "status": "运输中", "date": "2026-05-25"},
        {"order_id": "ORD003", "product": "MacBook Air", "price": 9499, "status": "已签收", "date": "2026-05-18"},
    ]
    
    import json
    return json.dumps(orders, ensure_ascii=False, indent=2)


def get_order_details(order_id: str) -> str:
    """
    获取特定订单的详细信息（商品、购买日期、物流等）
    
    Args:
        order_id: 订单 ID
    
    Returns:
        订单详细信息的 JSON 字符串
    """
    # 伪代码：实际项目中这里会调用订单详情 API
    print(f"[工具调用] get_order_details(order_id={order_id})")
    
    # 模拟返回数据
    order_details = {
        "order_id": order_id,
        "product": "iPhone 15 Pro",
        "price": 7999,
        "quantity": 1,
        "purchase_date": "2026-05-20",
        "status": "已签收",
        "shipping_address": "北京市朝阳区 xxx 街道",
        "logistics": "已签收，签收人：本人"
    }
    
    import json
    return json.dumps(order_details, ensure_ascii=False, indent=2)


def initiate_refund(order_id: str, reason: str) -> str:
    """
    正式发起退货流程
    
    Args:
        order_id: 订单 ID
        reason: 退货原因
    
    Returns:
        退货处理结果的 JSON 字符串
    """
    # 伪代码：实际项目中这里会调用退货 API，可能涉及库存、财务等系统
    print(f"[工具调用] initiate_refund(order_id={order_id}, reason={reason})")
    
    # 模拟返回数据
    result = {
        "success": True,
        "refund_id": f"REF{order_id[3:]}",
        "message": "退货申请已提交，预计 1-3 个工作日内处理",
        "refund_amount": 7999,
        "status": "审核中"
    }
    
    import json
    return json.dumps(result, ensure_ascii=False, indent=2)


def check_refund_policy(order_id: str) -> str:
    """
    检查订单是否符合退货政策
    
    Args:
        order_id: 订单 ID
    
    Returns:
        是否符合退货政策及原因
    """
    # 伪代码：检查退货期限、商品状态等
    print(f"[工具调用] check_refund_policy(order_id={order_id})")
    
    # 模拟返回数据
    return "符合退货政策：订单在 7 天无理由退货期内，商品未拆封"


# ========== 主程序 ==========

def test_after_sales_agent():
    """测试智能售后 Agent"""
    
    # 定义系统提示词
    system_prompt = """你是一个专业的电商售后客服助手。
你的目标是协助用户处理退货申请，并始终保持专业、高效且符合公司政策。"""
    
    # 定义可用工具
    tools = {
        "get_user_orders": get_user_orders,
        "get_order_details": get_order_details,
        "initiate_refund": initiate_refund,
        "check_refund_policy": check_refund_policy,
    }
    
    # 创建 Agent
    agent = MiniAgent(
        system_prompt=system_prompt,
        tools=tools
    )
    
    # 运行示例
    print("="*60)
    print("智能售后 Agent 启动")
    print("="*60)
    
    user_input = "我想退货，上周买的 iPhone"
    print(f"\n[用户]: {user_input}\n")
    
    result = agent.run(user_input)
    
    print(f"\n[最终结果]: {result}")


def testGLM():
    try:
        print(zai.__version__)
        client = ZhipuAiClient(api_key=os.getenv("ZAI_API_KEY"))
        response = client.chat.completions.create(
            model="glm-4.6v",
            messages=[
                {"role": "user", "content": "请帮我写一个..."}
            ]
        )
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"具体错误信息：{e}")


if __name__ == "__main__":
    # 运行售后 Agent
    test_after_sales_agent()
    
    # testGLM()
    # fetch_data()
    