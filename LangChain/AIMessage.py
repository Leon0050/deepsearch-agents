import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
load_dotenv(encoding="utf-8")

API_KEY = os.getenv("DEEPSEEK_API_KEY")

model = init_chat_model(
    model="deepseek-chat",
    model_provider="openai",
    api_key=API_KEY,
    base_url="https://api.deepseek.com",
    temperature=0.6,
    max_tokens=256,
)

user_input = input("请输入你的问题")

response = model.invoke(user_input)

print(response)
print(response.content)
print(type(model))             # 模型客户端对象
print(type(response))          # AIMessage
print(type(response.content))  # str