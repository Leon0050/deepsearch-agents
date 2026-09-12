import os
import dashscope
from dotenv import load_dotenv
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.graph_vectorstores.networkx import documents_to_networkx

load_dotenv(encoding="utf-8")
from langchain_core.documents import Document
from langchain_community.vectorstores import Redis
# dashscope.api_key = os.getenv("aliQwen-api")
# DeepSeek 目前没有 Embedding 模型
# 使用项目统一的 aliQwen-api；DashScopeEmbeddings 默认只读 DASHSCOPE_API_KEY，故显式传入
# embeddings = DashScopeEmbeddings(
#     model="deepseek-chat",  # deepseek-chat 是一个大语言模型（LLM），用于文本生成和对话，它不能用来生成文本向量（Embedding）
#     dashscope_api_key=os.getenv("DEEPSEEK_API_KEY"),
# )
embeddings = DashScopeEmbeddings(
    model="text-embedding-v4",
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"), # 确保 .env 中配置的是阿里云的 Key
)

text = "This is a test document."

# 单条文本 → 一个向量（列表）；这类写法更贴近“把用户问题转成查询向量”
query_result = embeddings.embed_query(text)
# sep=""：print 多个参数时用空字符串连接，默认是空格；这里让「文本向量长度：」和数字紧挨着输出，中间不留空
print("文本向量长度：", len(query_result), sep="")

# 多条文本 → 多个向量（列表的列表）；这类写法更贴近“批量建索引”
doc_results = embeddings.embed_documents(
    [
        "Hi there!",
        "Oh, hello!",
        "What's your name?",
        "My friends call me World",
        "Hello World!",
    ]
)
print(doc_results)
# sep=""：多个参数之间不加空格，输出如「文本向量数量：5，文本向量长度：1024」
print(
    "文本向量数量：", len(doc_results), "，文本向量长度：", len(doc_results[0]), sep=""
)

# 2. 构造 Document 列表：page_content 是正文，metadata 是附加信息
# 在完整 RAG 中，这些 Document 往往来自“加载器 + 分割器”；本案例先用手写数据聚焦理解向量库存取流程
texts = [
    "通义千问是阿里巴巴研发的大语言模型。",
    "Redis 是一个高性能的键值存储系统，支持向量检索。",
    "LangChain 可以轻松集成各种大模型和向量数据库。",
]

documents = [Document(page_content=text, metadata={"source":"manual"}) for text in texts]


# 3. 一次性写入 Redis：内部会对每个 Document 的 page_content 做向量化，并建立可检索索引
vector_store = Redis.from_documents(
    documents = documents,
    embeddings = embeddings,
    redis_url="redis://localhost:26379",
    index_name="my_index",
)

# 4. 得到检索器：当你 invoke 查询文本时，LangChain 会先把问题向量化，再在库中做相似度检索
retriever = vector_store.as_retriever(search_kwargs={"k":2})
results = retriever.invoke("LangChain 和 Redis 怎么结合？")
for res in results:
    print(res.page_content)