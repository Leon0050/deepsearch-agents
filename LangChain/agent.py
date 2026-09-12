import os
import json
import httpx
from pydantic import SecretStr
from pathlib import Path
from typing import TypedDict
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

@tool
def get_weather(loc:str) -> str:
    """
       查询即时天气函数
       :param loc: 城市英文名，如 Beijing、Shanghai。
       :return: OpenWeather API 返回的天气信息（JSON 字符串）。
       """
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": loc,
        "appid": os.getenv("OPENWEATHER_API_KEY"),
        "units": "metric",
        "lang": "zh_cn",
    }
    response = httpx.get(url, params=params, timeout = 30)
    data = response.json()
    return json.dumps(data, ensure_ascii=False)

# 定义结构化输出：Agent 最终回答会按此结构填充，便于代码中直接取字段
class WeatherCompareOutput(TypedDict):
    beijing_temp:float
    shanghai_temp:float
    hotter_city:str
    summary:str

api_key = os.getenv("OPENWEATHER_API_KEY")
if api_key is None:
    raise ValueError("OPENWEATHER_API_KEY 未配置")

model = ChatOpenAI(
    model= "qwen-plus",
    api_key=SecretStr(api_key),
    base_url= "https://dashscope.aliyuncs.com/compatible-mode/v1"
)

agent = create_agent(
    model = model,
    tools = [get_weather],
    system_prompt=(
        "你是天气助手。"
        "当用户询问天气时，"
        "你需要分别调用工具获取数据，并进行分析"
    ),
    response_format=WeatherCompareOutput
)

result = agent.invoke({"input":"请问今天北京和上海的天气怎么样，哪个城市更热？"})
print(result)
print()
print(json.dumps(result["structured_response"], ensure_ascii=False, indent=2))