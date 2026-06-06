import os
import uuid

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_core.stores import InMemoryStore
from langchain_classic.retrievers.multi_vector import MultiVectorRetriever
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.messages import HumanMessage


load_dotenv()

# 🚨 严格执行参谋长的 1.X 智谱平台初始化规范
# 在离线批量打标时，通常选用响应极快、成本极低的轻量多模态模型
tagger_model = ChatOpenAI(
    model='glm-4.6v-flash', # glm的免费模型
    openai_api_key=os.getenv("ZAI_API_KEY"),
    openai_api_base="https://open.bigmodel.cn/api/paas/v4/",
    temperature=0,
)
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3"
)

# 1. 初始化底座存储
vectorstore = FAISS.from_texts(["Initialization"], embeddings)
docstore = InMemoryStore()
multimodal_retriever = MultiVectorRetriever(vectorstore=vectorstore, docstore=docstore, id_key="doc_id")

# 2. 模拟后台自动扫描到了一张新的高清原始图片（例如：系统架构图）
raw_image_b64_incoming = "https://picx.zhimg.com/v2-2eadc5c4c31a5e45c6fc7b616288aa5f_r.webp?source=172ae18b&consumer=ZHI_MENG" 

# ==================== 🛠️ 3. 自动化流水线启动：智能打标 ====================
print("🤖 [自动化管道] 发现新图片，正在调度智谱多模态模型进行自动语义提炼...")

# 让多模态模型扮演高性能 OCR + 语义总结器的双重角色
tagger_message = HumanMessage(
    content=[
        {"type": "text", "text": "请作为数据打标器，为这张图片生成一段 100 字以内的精准文本摘要。必须包含图片的核心主题、关键数字、以及可能被用户搜索到的核心关键词。请直接输出摘要，不要带有任何客套话。"},
        {"type": "image_url", "image_url": {"url": raw_image_b64_incoming}}
    ]
)

# 自动生成摘要（替代了人工手写！）
auto_generated_summary = tagger_model.invoke([tagger_message]).content
print(f"📝 [自动打标成功] 生成的向量索引摘要为: \n-> '{auto_generated_summary}'\n")

# ==================== 💾 4. 自动指针持久化 ====================
image_doc_id = str(uuid.uuid4())

# 注入高维向量库（供在线检索检索）
summary_document = Document(page_content=auto_generated_summary, metadata={"doc_id": image_doc_id})
multimodal_retriever.vectorstore.add_documents([summary_document])

# 注入原始文档库（供在线查看恢复）
multimodal_retriever.docstore.mset([(image_doc_id, raw_image_b64_incoming)])

print("✅ [系统通知] 该多模态图片已成功建立双轨指针，全自动入库完毕。")