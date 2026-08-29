from langchain_core.output_parsers import JsonOutputParser
from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv(encoding="utf-8")
API_KEY= os.getenv("DEEPSEEK_API_KEY")

model = init_chat_model(
    model="deepseek-chat",
    model_provider="openai",
    api_key=API_KEY,
    base_url="https://api.deepseek.com",
    temperature=0.6,
    max_tokens=100,
    max_retries=3,
)

parser = JsonOutputParser()
result = model.invoke("请用 JSON 返回:age, 18")
data = parser.invoke(result)
# print(data)

class User(BaseModel):
    name: str
    age:int
