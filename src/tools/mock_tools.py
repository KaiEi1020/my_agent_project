import json
import os


def get_user_info() -> dict:
    """
    获取当前用户信息

    Returns:
        包含 userId 和乘机人姓名的用户信息字典
    """
    print("[工具调用] get_user_info()")
    user_id = os.getenv("USER_ID", "123")
    return {"userId": user_id, "name": "Edy", "passenger_name": "Edy"}


def get_user_orders(user_id: str, timeframe: str = "last_week") -> str:
    """
    查询用户在指定时间范围内的订单列表

    Args:
        user_id: 用户 ID
        timeframe: 时间范围，如 "last_week", "last_month"

    Returns:
        订单列表的 JSON 字符串
    """
    print(f"[工具调用] get_user_orders(user_id={user_id}, timeframe={timeframe})")

    if timeframe == "last_week":
        orders = [
            {
                "order_id": "ORD1001",
                "product": "红色衬衫",
                "sku": "SHIRT-RED-M",
                "price": 299,
                "status": "已签收",
                "date": "2026-05-28",
            },
            {
                "order_id": "ORD1002",
                "product": "蓝牙耳机",
                "sku": "EARBUDS-BLACK",
                "price": 699,
                "status": "已签收",
                "date": "2026-05-26",
            },
        ]
    else:
        orders = [
            {
                "order_id": "ORD001",
                "product": "iPhone 15",
                "price": 7999,
                "status": "已签收",
                "date": "2026-05-20",
            },
            {
                "order_id": "ORD002",
                "product": "AirPods Pro",
                "price": 1899,
                "status": "运输中",
                "date": "2026-05-25",
            },
            {
                "order_id": "ORD003",
                "product": "MacBook Air",
                "price": 9499,
                "status": "已签收",
                "date": "2026-05-18",
            },
        ]

    return json.dumps(orders, ensure_ascii=False, indent=2)


def get_order_details(order_id: str) -> str:
    """
    获取特定订单的详细信息（商品、购买日期、物流等）

    Args:
        order_id: 订单 ID

    Returns:
        订单详细信息的 JSON 字符串
    """
    print(f"[工具调用] get_order_details(order_id={order_id})")

    if order_id == "ORD1001":
        order_details = {
            "order_id": order_id,
            "product": "红色衬衫",
            "color": "红色",
            "size": "M",
            "price": 299,
            "quantity": 1,
            "purchase_date": "2026-05-28",
            "status": "已签收",
            "shipping_address": "杭州市西湖区 xxx 路 18 号",
            "logistics": "已签收，签收人：本人",
        }
    else:
        order_details = {
            "order_id": order_id,
            "product": "iPhone 15 Pro",
            "price": 7999,
            "quantity": 1,
            "purchase_date": "2026-05-20",
            "status": "已签收",
            "shipping_address": "北京市朝阳区 xxx 街道",
            "logistics": "已签收，签收人：本人",
        }

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
    print(f"[工具调用] initiate_refund(order_id={order_id}, reason={reason})")

    if order_id == "ORD1001":
        result = {
            "success": True,
            "refund_id": "REF1001",
            "message": "红色衬衫退货申请已提交，预计 1-3 个工作日内审核完成。",
            "refund_amount": 299,
            "status": "审核中",
        }
    else:
        result = {
            "success": True,
            "refund_id": f"REF{order_id[3:]}",
            "message": "退货申请已提交，预计 1-3 个工作日内处理",
            "refund_amount": 7999,
            "status": "审核中",
        }

    return json.dumps(result, ensure_ascii=False, indent=2)


def check_refund_policy(order_id: str) -> str:
    """
    检查订单是否符合退货政策

    Args:
        order_id: 订单 ID

    Returns:
        是否符合退货政策及原因
    """
    print(f"[工具调用] check_refund_policy(order_id={order_id})")

    if order_id == "ORD1001":
        return "符合退货政策：订单在 7 天无理由退货期内，商品保持完好，可发起退货。"
    return "符合退货政策：订单在 7 天无理由退货期内，商品未拆封"


def search_flights(destination: str, date_range: str) -> str:
    """
    查询指定时间范围内的航班信息

    Args:
        destination: 目的地
        date_range: 时间范围描述

    Returns:
        航班列表和天气信息的 JSON 字符串
    """
    print(f"[工具调用] search_flights(destination={destination}, date_range={date_range})")

    flights = [
        {
            "flight_no": "MU5137",
            "date": "2026-06-09",
            "from": "杭州",
            "to": destination,
            "depart_time": "09:30",
            "arrive_time": "10:35",
            "price": 680,
            "weather": "晴",
        },
        {
            "flight_no": "HO1188",
            "date": "2026-06-10",
            "from": "杭州",
            "to": destination,
            "depart_time": "14:20",
            "arrive_time": "15:25",
            "price": 620,
            "weather": "多云",
        },
        {
            "flight_no": "FM9452",
            "date": "2026-06-12",
            "from": "杭州",
            "to": destination,
            "depart_time": "08:10",
            "arrive_time": "09:15",
            "price": 590,
            "weather": "晴",
        },
    ]

    return json.dumps(flights, ensure_ascii=False, indent=2)


def book_flight(flight_no: str, passenger_name: str) -> str:
    """
    预订指定航班

    Args:
        flight_no: 航班号
        passenger_name: 乘机人姓名

    Returns:
        订票结果的 JSON 字符串
    """
    print(f"[工具调用] book_flight(flight_no={flight_no}, passenger_name={passenger_name})")

    result = {
        "success": True,
        "booking_id": "BK20260603001",
        "flight_no": flight_no,
        "passenger_name": passenger_name,
        "message": "已完成订票，请在出发前 2 小时到达机场。",
    }

    return json.dumps(result, ensure_ascii=False, indent=2)
