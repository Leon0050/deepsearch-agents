import os
from dotenv import load_dotenv
from langchain.chat_models import (
    init_chat_model,
)
load_dotenv(encoding="utf-8")
#实例化模型并调用
model = init_chat_model(
    model="qwen-plus",
    model_provider="openai",  # 使用 OpenAI SDK 格式
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
# 调用并直接取回复正文：invoke 返回消息对象，.content 为文本内容
print(model.invoke("你是谁？").content)
print("*"*30)

model2 = init_chat_model(
    model="deepseek-chat",
    model_provider="openai",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)
print(model2.invoke("我是谁").content)