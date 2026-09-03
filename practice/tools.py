from langchain.tools import tool
from loguru import logger
from pydantic import BaseModel, Field
import httpx
import os
import json
from dotenv import load_dotenv
load_dotenv(encoding="utf-8")


# 1
# @tool
# def add_number(a:int, b:int) -> int:
#     "两位整数相加"
#     return a+ b
#
# result = add_number.invoke({"a":1, "b":2})
# print(result)

# 2
# Pydantic 模型：定义“工具参数接口”，字段 description 会进入工具参数 schema
class FieldInfo(BaseModel):
    "定义加法运算所需参数"
    a:int = Field(description = "第1个参数")
    b:int = Field(description = "第2个参数")

# args_schema=FieldInfo：把参数模型绑定到工具，模型会更清楚看到 a、b 的类型与说明
@tool(args_schema= FieldInfo)
def add_number(a: int, b:int) -> int:
    "计算两个整数之和"
    return a+b

logger.info(f"name = {add_number.name}")
logger.info(f"args = {add_number.args}")
logger.info(f"description = {add_number.description}")
logger.info(f"return_direct = {add_number.return_direct}")
result = add_number.invoke({"a":1, "b":2})
print(result)
logger.info(result)

@tool
def get_weather(loc:str) -> str:
    """
        查询指定城市的即时天气。
    """
    url = "https://api.openweathermap.org/data/2.5/weather"
    params={
        "q":loc,
        "appid":os.getenv("OPENWEATHER_API_KEY"),
        "units":"metric",
        "lang":"zh_cn"
    }
    response = httpx.get(url, params=params, timeout=30)
    data = response.json()
    return json.dumps(data)

result = get_weather.invoke("Chuzhou")
print(result)

