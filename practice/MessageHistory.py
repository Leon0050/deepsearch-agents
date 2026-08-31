from dotenv import load_dotenv
load_dotenv(encoding="utf-8")
import os, redis
from loguru import logger
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableWithMessageHistory, RunnableConfig
from langchain_core.chat_history import InMemoryChatMessageHistory

llm = init_chat_model(
    model="deepseek-chat",
    model_provider="openai",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    temperature=0.6,
    max_tokens=300
)

# 提示模板：history 占位符用于注入历史消息，input 为当前用户输入
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个助手"),
        MessagesPlaceholder(variable_name="history"),
        ("human","{input}"),
    ]
)
parser = StrOutputParser()
chain = prompt | llm | parser
# 记忆组件：内存实现，进程内有效，重启后丢失
history = InMemoryChatMessageHistory()
# 包装链为「带历史」版本：本例固定返回同一个 history，重点先放在“自动读写历史”
runnable = RunnableWithMessageHistory(
    chain,
    get_session_history= lambda session_id: history,
    input_messages_key="input",
    history_messages_key="history",)
history.clear()
# 保留 session_id 配置，是为了让调用方式和 V2 / Redis 版保持一致
config = RunnableConfig(configurable={"session_id": "user-001"})

# 第一轮：写入「我叫张三，我爱好学习。」，模型回复后会自动写回 history
logger.info(runnable.invoke({"input": "我叫张三，我爱好学习。"}, config))
# runnable.invoke({"input": "What is my name?"}, config)
# 第二轮：history 中已有上一轮，模型能回答「叫什么、爱好是什么」
logger.info(runnable.invoke({"input": "我叫什么？我的爱好是什么？"}, config))
