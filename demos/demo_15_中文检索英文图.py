
import os
import uuid

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_core.stores import InMemoryStore # 🚨 纠正：1.x 标准核心存储导入
from langchain_community.vectorstores import FAISS
from langchain_classic.retrievers.multi_vector import MultiVectorRetriever

load_dotenv()

# ==========================================
# 🚨 严格执行参谋长双底座初始化规范
# ==========================================
model = ChatOpenAI(
    model=os.getenv("ZAI_MODEL"),
    openai_api_key=os.getenv("ZAI_API_KEY"),
    openai_api_base="https://open.bigmodel.cn/api/paas/v4/",
    temperature=0,
)

# 锁死 BAAI/bge-m3
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3"
)

# 1. 组装 1.x 规范下的双轨存储实体
vectorstore = FAISS.from_texts(["Initialization"], embeddings)
docstore = InMemoryStore() # 存放原始高清图

# 2. 实例化纯正 1.x 规范的多向量检索器
multimodal_retriever = MultiVectorRetriever(
    vectorstore=vectorstore,
    docstore=docstore,
    id_key="doc_id",
)

# 3. 模拟后台自动扫描到了一张英文的财务趋势图表
raw_image_b64_incoming = "https://images.stockfeel.com.tw/stockfeelimage/2016/12/%E5%A6%82%E4%BD%95%E9%96%B1%E8%AE%80%E7%BE%8E%E5%9C%8B%E5%85%AC%E5%8F%B8%E7%9A%84%E8%B2%A1%E5%A0%B110k-03.png" 

# ==================== 🛠️ 4. 离线流：BGE-M3 跨语言多模态打标 ====================
print("🤖 [自动化管道] 发现英文图表，正在调度智谱多模态模型进行‘跨语言语义提炼’...")

tagger_message = HumanMessage(
    content=[
        {"type": "text", "text": "请仔细看这张英文图表，直接用【中文】为它写一段 100 字以内的核心内容摘要。必须包含图表的核心宏观趋势和关键数据点，以便用户用中文能够精准搜索到。"},
        {"type": "image_url", "image_url": {"url": raw_image_b64_incoming }}
    ]
)

# 智谱大脑跨语言视界输出
chinese_summary = model.invoke([tagger_message]).content
print(f"📝 [跨语言自动打标成功] 生成的中文向量索引摘要为: \n-> '{chinese_summary}'\n")

# ==================== 💾 5. 纯正 1.x 双轨指针持久化 ====================
image_doc_id = str(uuid.uuid4())

# 轨道 A：中文摘要经由 BGE-M3 算成向量，绑定 ID 存入 FAISS
summary_document = Document(page_content=chinese_summary, metadata={"doc_id": image_doc_id})
multimodal_retriever.vectorstore.add_documents([summary_document])

# 轨道 B：原始英文高清图片存入大容量文档库
multimodal_retriever.docstore.mset([(image_doc_id, raw_image_b64_incoming)])

print("✅ [系统通知] 跨语言图文双轨指针建立完毕。用户现在可以用中文检索该英文图表了。")


# ==================== 🚀 6. 在线检索测试 ====================
print("\n" + "="*60)
print("🔍 [在线检索] 用户用中文提问...")
print("="*60)

query = "这张图表显示了什么趋势？"
print(f"\n📌 问题：'{query}'")

retrieved_docs = multimodal_retriever.invoke(query)
retrieved_image_url = retrieved_docs[0]

print(f"✅ 检索成功！图片 URL: {retrieved_image_url[:80]}...")
print(f"💡 说明：用户用中文提问，成功检索到英文图表！")

# ==================== 🤖 7. 终极测试：多模态 RAG 生成 ====================
print("\n" + "="*60)
print("🎯 [终极测试] 多模态 RAG 检索 + 智谱大脑作答")
print("="*60)

final_query = "请基于检索到的图表，用中文解释这张图的核心内容"
print(f"\n用户提问：'{final_query}'")

# 检索相关图片
retrieved_image = multimodal_retriever.invoke(final_query)[0]

# 组装多模态消息
rag_message = HumanMessage(
    content=[
        {"type": "text", "text": f"请严格基于这张检索到的图片回答用户问题：{final_query}"},
        {"type": "image_url", "image_url": {"url": retrieved_image}}
    ]
)

# 智谱多模态大脑作答
response = model.invoke([rag_message])

print("\n==== 🤖 最终多模态 RAG 输出 ====")
print(response.content)
print("\n✅ [演示完成] 跨语言多模态检索流水线成功运行！")

