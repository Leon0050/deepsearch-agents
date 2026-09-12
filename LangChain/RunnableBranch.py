from typing import Any
from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv
from loguru import logger
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableBranch, RunnableParallel

load_dotenv(encoding="utf-8")

# 英语分支：提示词模板 + 占位符 query
english_prompt = ChatPromptTemplate.from_messages(
    [("system","你是一个英语翻译专家，你叫小英"),("human", "{query}")]
)

japanese_prompt = ChatPromptTemplate.from_messages(
    [("system", "你是一个日语翻译专家，你叫小日"), ("human", "{query}")]
)

korean_prompt = ChatPromptTemplate.from_messages(
    [("system", "你是一个韩语翻译专家，你叫小韩"), ("human", "{query}")]
)



def determine_language(inputs):
    """根据 query 中的关键词判断语言类型，供分支条件使用。"""
    query = inputs["query"]
    if "日语" in query:
        return "japanese"
    elif "韩语" in query:
        return "korean"
    else:
        return "english"


model = init_chat_model(
    model="deepseek-chat",
    model_provider="openai",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)
parser= StrOutputParser()

# RunnableBranch( (条件1, 子链1), (条件2, 子链2), ..., 默认子链 )
# 条件为可调用对象，接收输入 dict，返回 bool；第一个命中的分支会执行，最后一个参数是默认分支
chain = RunnableBranch(
    (lambda x: determine_language(x) == "japanese",  japanese_prompt | model | parser),
              (lambda x: determine_language(x) == "korean", korean_prompt | model | parser),
        (english_prompt | model | parser),  # 默认分支：英语
)

test_queries = [
    {"query": '请你用韩语翻译这句话:"见到你很高兴"'},
    {"query": '请你用日语翻译这句话:"见到你很高兴"'},
    {"query": '请你用英语翻译这句话:"见到你很高兴"'},
]

for query_input in test_queries:
    lang = determine_language(query_input)
    logger.info(f"检测到语言类型: {lang}")

    if lang == "japanese":
        chatPromptTemplate = japanese_prompt
    elif lang == "korean":
        chatPromptTemplate = korean_prompt
    else:
        chatPromptTemplate = english_prompt

    # 仅作演示：格式化后的提示词内容（实际执行时由 chain.invoke 内部完成）
    formatted_messages = chatPromptTemplate.format_messages(**query_input)
    logger.info("格式化后的提示词:")
    for msg in formatted_messages:
        logger.info(f"[{msg.type}]: {msg.content}")

    # 一次 invoke：Branch 会根据 query 自动选分支并执行对应子链
    result = chain.invoke(query_input)
    logger.info(f"输出结果: {result}\n")

"""
【输出示例】
2026-03-06 10:15:54.493 | INFO     | __main__:<module>:77 - 检测到语言类型: korean
2026-03-06 10:15:54.493 | INFO     | __main__:<module>:88 - 格式化后的提示词:
2026-03-06 10:15:54.493 | INFO     | __main__:<module>:90 - [system]: 你是一个韩语翻译专家，你叫小韩
2026-03-06 10:15:54.493 | INFO     | __main__:<module>:90 - [human]: 请你用韩语翻译这句话:"见到你很高兴"
2026-03-06 10:15:55.733 | INFO     | __main__:<module>:94 - 输出结果: 만나서 반갑습니다.

# 2026-03-06 10:15:55.733 | INFO     | __main__:<module>:77 - 检测到语言类型: japanese
# 2026-03-06 10:15:55.733 | INFO     | __main__:<module>:88 - 格式化后的提示词:
# 2026-03-06 10:15:55.733 | INFO     | __main__:<module>:90 - [system]: 你是一个日语翻译专家，你叫小日
# 2026-03-06 10:15:55.733 | INFO     | __main__:<module>:90 - [human]: 请你用日语翻译这句话:"见到你很高兴"
# 2026-03-06 10:15:56.552 | INFO     | __main__:<module>:94 - 输出结果: お会いできて嬉しいです。

# 2026-03-06 10:15:56.552 | INFO     | __main__:<module>:77 - 检测到语言类型: english
# 2026-03-06 10:15:56.552 | INFO     | __main__:<module>:88 - 格式化后的提示词:
# 2026-03-06 10:15:56.552 | INFO     | __main__:<module>:90 - [system]: 你是一个英语翻译专家，你叫小英
# 2026-03-06 10:15:56.552 | INFO     | __main__:<module>:90 - [human]: 请你用英语翻译这句话:"见到你很高兴"
# 2026-03-06 10:15:57.031 | INFO     | __main__:<module>:94 - 输出结果: Nice to meet you.

"""
prompt1 = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个知识渊博的计算机专家，请用中文简短回答"),
        ("human", "请简短介绍什么是{topic}"),
    ]
)
parser1 = StrOutputParser()
chain1 = prompt1 | model | parser1

# 子链 2：英文简短介绍（与 chain1 同结构，仅提示词语言不同）
prompt2 = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个知识渊博的计算机专家，请用英文简短回答"),
        ("human", "请简短介绍什么是{topic}"),
    ]
)
parser2 = StrOutputParser()
chain2 = prompt2 | model | parser2

# RunnableParallel：同一输入会同时喂给多个子链，结果按键汇总为 dict
parallel_chain = RunnableParallel({"chinese": chain1, "english": chain2})

parallel_chain = RunnableParallel(
    {"chinese":chain1,
     "english":chain2
     }
)

# parallel_chain = RunnableParallel({
#     "chinese":chain1,
#     "english":chain2
# })
# 一次 invoke，返回 {"chinese": "...", "english": "..."}
result = parallel_chain.invoke({"topic": "langchain"})
logger.info(result)

# 可选：打印并行链的 ASCII 图结构，便于理解“并行节点 + 汇总输出”的数据流
parallel_chain.get_graph().print_ascii()

"""
【输出示例】
2026-03-06 10:28:37.853 | INFO     | __main__:<module>:54 - {'chinese': 'LangChain 是一个开源框架，用于构建基于大语言模型（LLM）的应用程序。它提供模块化组件（如链（Chains）、提示模板、记忆（Memory）、工具（Tools）和数据连接器），帮助开发者轻松实现提示工程、外部数据检索（RAG）、多步推理、对话状态管理等功能，提升 LLM 应用的可控性、可扩展性和实用性。', 'english': 'LangChain is a framework for developing applications powered by large language models (LLMs), enabling chaining of prompts, LLM calls, and external tools (e.g., APIs, databases) to build complex, stateful, and context-aware workflows.'}
            +--------------------------------+
            | Parallel<chinese,english>Input |
            +--------------------------------+
                   ***               ***
                ***                     ***
              **                           **
+--------------------+              +--------------------+
| ChatPromptTemplate |              | ChatPromptTemplate |
+--------------------+              +--------------------+
           *                                   *
           *                                   *
           *                                   *
    +------------+                      +------------+
    | ChatOpenAI |                      | ChatOpenAI |
    +------------+                      +------------+
           *                                   *
           *                                   *
           *                                   *
  +-----------------+                 +-----------------+
  | StrOutputParser |                 | StrOutputParser |
  +-----------------+                 +-----------------+
                   ***               ***
                      ***         ***
                         **     **
            +---------------------------------+
            | Parallel<chinese,english>Output |
            +---------------------------------+
"""

from langchain_core.runnables import RunnableLambda

def debug_print(x):
    print(x)
    return {"input": x}
chain = chain1 | RunnableLambda[Any, dict[str, Any]](debug_print)| chain2



