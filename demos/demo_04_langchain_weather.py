# 导入 LangChain 的标准模型接口
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv
from langchain_core.tools import tool


load_dotenv()

@tool
def check_weather(city: str) -> str:
    """这是一个查天气的工具。当你需要了解某个城市未来的天气状况时，请调用它。
    
    Args:
        city: 目标城市的名称，例如 '北京'、'三亚'。
    """
    # 这里写你真正的业务 Python 代码，比如请求高德天气 API
    return f"{city}接下来几天都是晴天，气温25度，非常适合出行。"

# 1. 声明模型（只需在这里切换底层，后面代码完全不动）
model = ChatOpenAI(
    model=os.getenv("ZAI_MODEL"),
    openai_api_key=os.getenv("ZAI_API_KEY"),
    temperature=0,
    openai_api_base="https://open.bigmodel.cn/api/paas/v4/"
)
# model_with_tools = model.bind_tools([check_weather])

# 如果想换 DeepSeek，只需要：
# from langchain_deepseek import ChatDeepSeek
# model = ChatDeepSeek(model="deepseek-chat", temperature=0)

# 2. 声明一个可复用的标准 Prompt 模版
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的{role}助理。"),
    ("user", "{content}")
])

# 3. 用 LCEL 管道符组装一条“链 (Chain)”
agent_chain = prompt_template | model

# 4. 运行
response = agent_chain.invoke({
    "role": "旅游管家",
    "content": "帮我看看下周上海的天气"
})

print(response.content) # 拿到标准化的返回