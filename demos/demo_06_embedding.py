from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

# 1. 模拟那本 30 万字手册的其中一小段文本
raw_document = """
云原生科技公司员工守则：
第一条，关于假期。凡是入职满一年的正式员工，每年可享受 5 天的带薪年假。
第二条，关于报销。差旅补贴每日最高 300 元，需凭发票在次月 5 日前提交系统审批。
第三条，关于考勤。弹性工作制，每日打满 8 小时即可。
"""

# 2. 初始化一个聪明的切片器：每个切片最多 80 字，重叠 20 字
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=80,
    chunk_overlap=20,
    length_function=len
)

# 3. 开始切片
chunks = text_splitter.split_text(raw_document)
print(f"✂️ 成功将文档切成了 {len(chunks)} 个小段落。")
for i, chunk in enumerate(chunks):
    print(f"段落 [{i}]: {chunk}")

# 4. 初始化 Embedding 大脑（准备将文字降维打击成数字） TODO: 没有配置环境变量，会报错
embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")

# 5. 试着把第一个段落转成向量
first_chunk_vector = embeddings_model.embed_query(chunks[0])
print(f"\n🔢 段落 [0] 转化为向量后的维度: {len(first_chunk_vector)}")
print(f"向量前 5 个数字长这样: {first_chunk_vector[:5]}")