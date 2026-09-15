import time
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.cache.memory import InMemoryCache
from langgraph.types import CachePolicy

import time
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, START, END
from langgraph.cache.memory import InMemoryCache
from langgraph.types import CachePolicy

class State(TypedDict):
    x:int
    result:int

builder = StateGraph(State)

def expensive_node(state: State) -> dict[str, int]:
    """模拟耗时计算（sleep 3 秒），用于观察缓存命中时不再执行。"""
    time.sleep(3)
    return {"result": state["x"] * 2}

# 为该节点配置缓存，ttl=8 秒
builder.add_node(
    node="expensive_node",
    action=expensive_node,
    cache_policy=CachePolicy(ttl=8),
)

builder.set_entry_point("expensive_node")
builder.set_finish_point("expensive_node")

# 编译时指定使用内存缓存
app = builder.compile(cache=InMemoryCache())

# 第一次执行：无缓存，耗时约 3 秒
print("第一次执行（无缓存，耗时 3 秒）：")
print(app.invoke({"x": 5}))

# 第二次执行：命中缓存，立即返回
print("\n第二次运行利用缓存并快速返回：")
print(app.invoke({"x": 5}))

# 等待 ttl 过期后再次执行，将重新计算
print("\n等待 8 秒，缓存过期...")
time.sleep(8)
print("8 秒后第三次执行（重新计算，耗时 3 秒）：")
print(app.invoke({"x": 5}))

"""
【输出示例】
第一次执行（无缓存，耗时 3 秒）：
{'x': 5, 'result': 10}

第二次运行利用缓存并快速返回：
{'x': 5, 'result': 10}

等待 8 秒，缓存过期...
8 秒后第三次执行（重新计算，耗时 3 秒）：
{'x': 5, 'result': 10}
"""
