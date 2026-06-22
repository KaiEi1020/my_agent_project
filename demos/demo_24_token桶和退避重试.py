from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_openai import ChatOpenAI

# 1. 🛡️ 初始化一个标准的 Token 桶速率限制器（事前预防）
# 假设大模型网关限制我们每秒最多只能发 2 个请求（requests_per_second=2）
# max_bucket_size=10 意味着：突发流量时，桶里最多攒 10 个令牌供突发消费
rate_limiter = InMemoryRateLimiter(
    requests_per_second=2.0,
    max_bucket_size=10,
    check_every_n_seconds=0.1 # 每 100ms 检查一次桶里有没有新令牌
)

# 2. 🚀 将防御盾牌直接注入大模型客户端
safe_llm = ChatOpenAI(
    model="gpt-4o",
    timeout=30.0,
    
    # 【组合拳第一打】：内置的指数退避重试（事后补救）
    max_retries=5,  # 遇到 429 会自动启动带 Jitter 的指数退避重试，不需要再手动手写 tenacity 装饰器
    
    # 【组合拳第二打】：绑定我们定义好的 Token 桶（事前平滑）
    rate_limiter=rate_limiter 
)

# 这样配置后，你的多 Agent 网络在调用 safe_llm 时，会自动实现：
# 1. 发送前先去 rate_limiter 申请令牌，不够就排队（平滑流量）。
# 2. 偶尔因外部网络抖动漏掉的 429 报错，自动触发 5 次指数退避重试。