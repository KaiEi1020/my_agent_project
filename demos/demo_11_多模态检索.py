import os
import uuid

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_core.stores import InMemoryStore
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_classic.retrievers.multi_vector import MultiVectorRetriever

load_dotenv()

# 🚨 严格执行参谋长的 1.X 智谱平台初始化规范
model = ChatOpenAI(
    model=os.getenv("ZAI_MODEL"),  # 必须配置为支持多模态输入的模型
    api_key=os.getenv("ZAI_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4/",
    temperature=0,
)
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3"
)

# 1. 初始化双轨存储实体
vectorstore = FAISS.from_texts(["初始化占位"], embeddings) # 核心向量库
docstore = InMemoryStore() # 存放原始大文件/图像的文档库
id_key = "doc_id"

# 2. 实例化 1.x 标准多向量检索器
multimodal_retriever = MultiVectorRetriever(
    vectorstore=vectorstore,
    docstore=docstore,
    id_key=id_key,
)

# 3. 模拟录入一条多模态知识：一张复杂的财务柱状图 TODO: 图片格式不对 llm 抛错
raw_image_b64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..." # 原始高清图
image_summary = "图表：2025年公司四个季度的营业收入对比柱状图。Q1为10M，Q2为15M，Q4冲高至30M。"

# 4. 离线入库：双轨指针绑定
image_doc_id = str(uuid.uuid4())

# 轨道 A：把摘要算成向量，绑定 ID，存入向量库
summary_doc = Document(page_content=image_summary, metadata={id_key: image_doc_id})
multimodal_retriever.vectorstore.add_documents([summary_doc])

# 轨道 B：把原始高清图片，绑定相同的 ID，存入文档库
multimodal_retriever.docstore.mset([(image_doc_id, raw_image_b64)])
print("💾 [离线入库] 成功完成多模态图文指针双轨持久化！")


# ==================== 🚀 5. 在线检索与终极多模态生成 ====================
query = "帮我看看公司去年哪个季度的营收最高？具体是多少？"
print(f"\n🔍 [在线实时检索] 用户提问: '{query}'")

# 一键通过摘要向量，捞出底层的原始高清图片数据！
retrieved_raw_images = multimodal_retriever.invoke(query)
target_image_b64 = retrieved_raw_images[0]

# 组装 1.x 多模态输入负载，把捞出来的原始图片直接怼给多模态大模型的大脑
final_rag_message = HumanMessage(
    content=[
        {"type": "text", "text": f"请严格基于这张捞出来的原始知识库图表，回答用户问题：{query}"},
        {"type": "image_url", "image_url": {"url": target_image_b64}}
    ]
)

# 交付智谱多模态大脑作答
response = model.invoke([final_rag_message])
print("\n==== 🤖 最终多模态 RAG 的高保真输出 ====")
print(response.content)