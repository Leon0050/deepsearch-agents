# from typing import TypedDict
# from langgraph.graph import StateGraph, START, END
# import uuid
#
# # 1. 定义 State（状态）：声明图中要传递的字段及类型（可选）
# class HelloState(TypedDict):
#     name: str
#     greeting: str
#
# # 2. 定义节点函数 Node：接收当前 state，返回对 state 的「部分更新」字典
# def greet(helloState: HelloState) -> dict:
#     name = helloState["name"]
#     return {"greeting": f"你好，{name}"}
#
# def add_emoji(helloState: HelloState) -> dict:
#     greeting = helloState["greeting"]
#     return {"greeting": greeting + "。。。😄"}
#
# # 3. 构建图 Graph：初始化 StateGraph，添加节点与边
# graph = StateGraph(HelloState)
# graph.add_node("greeting", greet)
# graph.add_node("add_emoji", add_emoji)
# graph.add_edge(START, "greeting")
# graph.add_edge("greeting", "add_emoji")
# graph.add_edge("add_emoji",END)
#
# # 4. 编译图，得到可执行的 app
# app = graph.compile()
#
# # 5. 运行：invoke 只接收一个核心参数——初始状态字典
# # result = app.invoke({"name": "z3"})
# result = app.invoke({"name": "z3"})
# print(result)
# print(result["greeting"])
#
# # 6. 可视化：ASCII 和 Mermaid 两种方式最适合入门阶段快速看图结构
# # print(app.get_graph().print_ascii())
# print(app.get_graph().print_ascii())
# print("=" * 50)
# # print(app.get_graph().draw_mermaid())
# print(app.get_graph().draw_mermaid())
# print("=" * 50)

# # 可选：生成 PNG 图片（依赖 mermaid.ink 或 Pyppeteer，易受网络影响）
# png_bytes = app.get_graph().draw_mermaid_png(max_retries=2, retry_delay=2.0)
# output_path = "langgraph" + str(uuid.uuid4())[:8] + ".png"
# with open(output_path, "wb") as f:
#     f.write(png_bytes)
# print(f"图片已生成：{output_path}")

"""
【输出示例】
{'name': 'z3', 'greeting': '你好,z3  。。。😄'}
你好,z3  。。。😄
（图中 __start__ / __end__ 及 Python 属性命名约定见文件头「知识点速览」。）

+-----------+
| __start__ |
+-----------+
      *
      *
      *
+----------+
| greeting |
+----------+
      *
      *
      *
+-----------+
| add_emoji |
+-----------+
      *
      *
      *
 +---------+
 | __end__ |
 +---------+
None
==================================================
---
config:
  flowchart:
    curve: linear
---
graph TD;
        __start__([<p>__start__</p>]):::first
        greeting(greeting)
        add_emoji(add_emoji)
        __end__([<p>__end__</p>]):::last
        __start__ --> greeting;
        greeting --> add_emoji;
        add_emoji --> __end__;
        classDef default fill:#f2f0ff,line-height:1.2
        classDef first fill-opacity:0
        classDef last fill:#bfb6fc
"""

# from langgraph.constants import START, END
# from langgraph.graph import StateGraph
from langgraph.graph import StateGraph
from langgraph.constants import START, END

def addition(state):
    """加法节点：将 state 中的 x 加 1。"""
    print(f"加法节点收到的初始值:{state}")
    return {"x": state["x"] + 1}

def subtraction(state):
    """减法节点：将 state 中的 x 减 2。"""
    print(f"减法节点收到的初始值:{state}")
    return {"x": state["x"] - 2}

# 使用 dict 作为状态类型，无需预定义 TypedDict
graph = StateGraph(dict)
graph.add_node("addition", addition)
graph.add_node("subtraction", subtraction)

# 定义执行顺序：START → addition → subtraction → END
graph.add_edge(START, "addition")
graph.add_edge("addition", "subtraction")
graph.add_edge("subtraction", END)

# 查看图的边与节点（调试用）
print(graph.nodes)
print(graph.edges)

# 编译图构建器，得到可执行的图应用对象
# app = graph.compile()
app = graph.compile()
# invoke() 的核心输入是一整个状态字典，这里给 x 一个初始值 5
# initial_state = {"x": 5}
initial_state = {"x" : 6}
# invoke 只接收一个核心参数：初始状态字典
result = app.invoke(initial_state)
print(f"最后的结果是:{result}")

# 打印图的可视化结构
print(app.get_graph().print_ascii())
print()
# 打印图的可视化结构，生成更加美观的Mermaid 代码，通过processon 编辑器查看
print(app.get_graph().draw_mermaid())
