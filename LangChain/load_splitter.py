# pip install langchain_community
from langchain_community.document_loaders import TextLoader, PyPDFLoader,UnstructuredWordDocumentLoader, UnstructuredMarkdownLoader, JSONLoader, CSVLoader


# file_path = "assets/sample.txt"
# encoding = "utf-8"
#
# # load() 为 BaseLoader 统一接口，返回 List[Document]
# docs = TextLoader(file_path, encoding).load()
#
# docs2 = PyPDFLoader(
#     file_path = "assets/sasmple.pdf",
#     extraction_mode="plain",  # plain 纯文本；layout 按版面
# ).load()
#
# docs3 = UnstructuredWordDocumentLoader(
# # docs4 = UnstructuredMarkdownLoader(
#     file_path ="assets/sample.docx",
#     mode = "single", # single 整篇一个 Document；elements 按元素切分
# ).load()
#
# docs5 = JSONLoader(
#     file_path="assets/sample.json",
#     jq_schema=".",  # 提取所有字段
#     text_content=False, # 是否按字符串处理内容
# ).load()
#
# # docs6 = CSVLoader(file_path="assets.sample.csv").load()
# docs6 = CSVLoader(
#     file_path="assets/sample.csv",
#     metadata_columns=["title","author"],
#     content_columns=["content"],
# ).load()
#
# print(docs)

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_unstructured import UnstructuredLoader

# loader = UnstructuredLoader("rag.txt")
# documents = loader.load()
# 1. 待分割的原文
content = (
    "大模型RAG（检索增强生成）是一种结合生成模型与外部知识检索的技术，通过从大规模文档或数据库中检索相关信息，"
    "辅助生成模型以提升回答的准确性和相关性。其核心流程包括用户输入查询、系统检索相关知识、"
    "生成模型基于检索结果生成内容，并输出最终答案。RAG的优势在于能够弥补生成模型的知识盲区，"
    "提供更准确、实时和可解释的输出，广泛应用于问答系统、内容生成、客服、教育和企业领域。"
    "然而，其也面临依赖高质量知识库、可能的响应延迟、较高的维护成本以及数据隐私等挑战。"
)

# # 2. 分割器：块大小 100 字符，重叠 30 字符，长度按 len（字符数）计算
# text_splitter = RecursiveCharacterTextSplitter(
#     chunk_size=100, chunk_overlap=20, length_function=len
# )
#
# # 3. 先切成字符串列表
# splitter_texts = text_splitter.split_text(content)
#
# # 4. 再转成 Document 列表（便于后续与向量库、检索器对接）
# splitter_documents = text_splitter.create_documents(splitter_texts)
#
# print(f"原始文本大小：{len(content)}")
# print(f"分割文档数量：{len(splitter_documents)}")
# for splitter_document in splitter_documents:
#     print(
#         f"文档片段大小：{len(splitter_document.page_content)},文档内容：{splitter_document.page_content}"
#     )

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100, chunk_overlap=30, length_function=len
)

# 先 split_text，再手动转 Document：这里这样写只是为了把“字符串块 -> Document”这一步显式展示出来
splitter_texts = text_splitter.split_text(content)
splitter_documents = [Document(page_content=text) for text in splitter_texts]

# 剔除重叠部分后拼接，用于验证与原文一致；这里直接写死 30，是因为前面 chunk_overlap=30
full_content = ""
for text in splitter_texts:
    if full_content:
        full_content += text[30:]
    else:
        full_content += text

print(f"原始文本大小：{len(content)}，原始内容：\n{content}\n")
print(f"分割文档数量：{len(splitter_documents)}\n")
for idx, splitter_document in enumerate(splitter_documents, 1):
    print(
        f"第{idx}个文档 - 大小：{len(splitter_document.page_content)}, 内容：{splitter_document.page_content}\n"
    )

print(f"拼接后文本大小：{len(full_content)}")
print(f"是否与原始文本完全一致：{full_content == content}")
print(f"拼接后完整内容：\n{full_content}")