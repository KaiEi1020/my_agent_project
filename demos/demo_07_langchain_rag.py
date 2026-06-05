import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

# 1. 在线阶段：假设我们已经从磁盘捞出了那段【手册丙】
retrieved_context = "手册丙内容：员工每年有五天不用上班，公司照样发工资。"
user_query = "我想请假，今年我有几天带薪假？"

# 2. 用 LangChain 包装我们的标准开卷考试 Prompt
prompt = ChatPromptTemplate.from_template("""
你是一个基于公司内部知识库回答问题的助理。请严格根据【已知参考资料】回答【用户问题】。
如果资料里没有，就说不知道，严禁瞎编。

【已知参考资料】
{retrieved_context}

【用户问题】
{user_query}
""")

# RAG 场景通常把温控设为 0，追求极度严谨
model = ChatOpenAI(
    model=os.getenv("ZAI_MODEL"),
    openai_api_key=os.getenv("ZAI_API_KEY"),
    temperature=0,
    openai_api_base="https://open.bigmodel.cn/api/paas/v4/"
)

# 4. LCEL
rag_chain = prompt | model | StrOutputParser()

# 5. 一键发射！
final_answer = rag_chain.invoke({
    "retrieved_context": retrieved_context,
    "user_query": user_query
})

print("==== 🤖 大模型闭卷转开卷后的完美回复 ====")
print(final_answer)