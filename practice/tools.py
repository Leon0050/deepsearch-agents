from langchain.tools import tool
from loguru import logger
from pydantic import BaseModel, Field

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