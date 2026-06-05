import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

print('ZAI_MODEL', os.getenv("ZAI_MODEL"))

# ==========================================
# 🚨 严格执行参谋长的 1.X 智谱平台初始化规范
# ==========================================
model = ChatOpenAI(
    model=os.getenv("ZAI_MODEL"),
    openai_api_key=os.getenv("ZAI_API_KEY"),
    openai_api_base="https://open.bigmodel.cn/api/paas/v4/",
    temperature=0,
)

# 2. 用 1.x 标准结构组装多模态消息 (Text + Image Mix)
multimodal_message = HumanMessage(
    content=[
        # 视觉输入
        {
            "type": "image_url",
            "image_url": {
              "url": "https://cdn.bigmodel.cn/static/logo/api-key.png"
            }
        },
        # 文本提示词
        {
            "type": "text", 
            "text": "请仔细分析这张图片里的架构图，用结构化的 markdown 列表告诉我：1. 这个架构分为了哪几层？2. 核心组件有哪些？"
        }
    ]
)

# 3. 注入系统防御性提示词，防止视觉幻觉
system_message = SystemMessage(
    content="""你是一个高精度的企业级视觉数据审计助理。
在你分析图片时，必须严格遵守以下【视觉红线】：
1. 任何图片局部、文字、连线由于分辨率低、反光、遮挡导致【看不清】或【有歧义】的，【严禁】结合上下文进行逻辑推导和合理猜测。
2. 针对看不清的区域，你必须直接在报告中写出：'[🚨 区域模糊，无法识别]'。
3. 宁可不汇报，也绝对不允许出现任何脑补、自行补充的组件名。
"""
)

# 4. 一键触发视觉理解
print("👁️ 正在把图像数据和提示词打包发送至智谱多模态端点...")
response = model.invoke([system_message, multimodal_message])

print("\n==== 🤖 多模态 Agent 视觉分析报告 ====")
print(response.content)