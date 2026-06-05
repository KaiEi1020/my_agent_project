# ==========================================
# 🚨 LANGCHAIN 1.X 标准工业级导入规范
# ==========================================
import os

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings

# 从社区库中精准导入现代 1.x 兼容的组件
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain_community.document_compressors import FlashrankRerank
from langchain_classic.retrievers import (
    ContextualCompressionRetriever,
    EnsembleRetriever,
)

load_dotenv()

# 1. 初始化 1.x 统一大模型大脑与向量引擎
model = ChatOpenAI(
    model=os.getenv("ZAI_MODEL"),
    openai_api_key=os.getenv("ZAI_API_KEY"),
    openai_api_base="https://open.bigmodel.cn/api/paas/v4/",
    temperature=0,
)
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3"
)

# 2. 本地测试语料
docs = [
    Document(page_content="张三在 2026 年请了 5 天病假办理医疗报销。", metadata={"source": "HR-001"}),
    Document(page_content="李四在 2026 年出差上海 3 天，不涉及请假。", metadata={"source": "HR-002"}),
    Document(page_content="张三拒绝了李四的请假申请，因为项目进度吃紧。", metadata={"source": "HR-003"}) # 内鬼数据
]

# 3. 组装 1.x 多路召回（Hybrid Search）
bm25_retriever = BM25Retriever.from_documents(docs)
bm25_retriever.k = 2

faiss_db = FAISS.from_documents(docs, embeddings)
vector_retriever = faiss_db.as_retriever(search_kwargs={"k": 2})

# 使用 RRF 算法融合成集成检索器（两路各占 50% 权重）
hybrid_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.5, 0.5]
)

# 4. 挂载 1.x 严谨重排层（Reranker），剔除内鬼语义，精选最优的 2 条
reranker = FlashrankRerank(model="ms-marco-MultiBERT-L-12", top_n=2)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=reranker, 
    base_retriever=hybrid_retriever
)

# 5. 1.x 标准声明式 LCEL 链条：将检索与生成无缝绑定
# 这一步展示了 1.x 优雅的“数据流思想”，将整个 RAG 变成一个开卷考试闭环
rag_prompt = ChatPromptTemplate.from_template("""请严格根据【已知参考资料】回答【用户问题】。
如果资料里没有提供确切信息，请直接回答不知道，严禁瞎编。

【已知参考资料】
{context}

【用户问题】
{question}
""")

# 自动化上下文提取函数
def format_docs(retrieved_docs):
    return "\n\n".join(doc.page_content for doc in retrieved_docs)


def build_context(inputs):
    question = inputs["question"]
    hybrid_docs = hybrid_retriever.invoke(question)
    retrieved_docs = reranker.compress_documents(hybrid_docs, question)

    print("\n===== RRF 后结果 =====")
    for index, doc in enumerate(hybrid_docs, start=1):
        source = doc.metadata.get("source", "UNKNOWN")
        print(f"[{index}] source={source} content={doc.page_content}")

    print("\n===== 重排后结果 =====")
    for index, doc in enumerate(retrieved_docs, start=1):
        source = doc.metadata.get("source", "UNKNOWN")
        score = doc.metadata.get("relevance_score")
        if score is not None:
            print(f"[{index}] source={source} score={score:.4f} content={doc.page_content}")
        else:
            print(f"[{index}] source={source} content={doc.page_content}")

    return format_docs(retrieved_docs)


# 用 1.x 管道符组装终极流水线
# 当调用 invoke 时，会先通过压缩检索器捞数据，再格式化，最后送给 Prompt 和模型
complete_rag_chain = (
    {
        "context": build_context,
        "question": lambda x: x["question"],
    }
    | rag_prompt
    | model
    | StrOutputParser()
)

# 6. 一键启动测试
user_query = "张三在 2026 年一共请了几天假？"
final_answer = complete_rag_chain.invoke({"question": user_query})

print(f"🎯 用户问题: '{user_query}'")
print(f"🤖 LangChain 1.x 管道流最终给出的高质量安全回复：\n{final_answer}")