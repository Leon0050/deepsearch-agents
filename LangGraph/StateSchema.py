# from typing import Annotated, TypedDict
# from langgraph.graph import StateGraph,START,END
#
# # 定义状态：process_data 用于在节点间传递；本例未指定 Reducer，因此后续节点会按默认覆盖规则更新它
# class GraphState(TypedDict):
#     process_data: str
#
# def input_node(state:GraphState)-> dict:
#     """入口节点：写入初始 process_data。"""
#     print(f"input_node 节点执行 state.get('process_data'): {state.get('process_data')}")
#     return {"process_data": {"input": "input_value"}}
#
# def process_node(state: dict) -> dict:
#     """处理节点：更新 process_data。"""
#     print(
#         f"process_node 节点执行 state.get('process_data'): {state.get('process_data')}"
#     )
#     return {"process_data": {"process": "process_value9527"}}
#
#
# def output_node(state: GraphState) -> dict:
#     """出口节点：读取并返回当前 process_data。"""
#     print(
#         f"output_node 节点执行 state.get('process_data'): {state.get('process_data')}"
#     )
#     return {"process_data": state.get("process_data")}
#
#
# # 创建状态图并指定状态类型
# graph = StateGraph(GraphState)
# graph.add_node("input", input_node)
# graph.add_node("process", process_node)
# graph.add_node("output", output_node)
#
# # 固定边：start → input → process → output → end
# graph.add_edge(START, "input")
# graph.add_edge("input", "process")
# graph.add_edge("process", "output")
# graph.add_edge("output", END)
#
# # 编译后执行；传入的初始 state 会与各节点返回值按 Reducer 规则合并
# app = graph.compile()
# result = app.invoke({"process_data": {"name": "测试数据", "value": 123456}})
# print(f"最后的结果是:{result}")
#
# # 可视化
# print(app.get_graph().print_ascii())
# print("=================================")
# print(app.get_graph().draw_mermaid())

from langgraph.graph import StateGraph,START, END
from typing_extensions import TypedDict
from typing import TypedDict
from pydantic import BaseModel


# 仅包含「输入」字段的 Schema：限制调用方进图时能传什么
class InputState(TypedDict):
    question: str

# 仅包含「输出」字段的 Schema：限制图最终对外返回什么
class OutputState(TypedDict):
    answer: str

# 图内部使用的完整 State Schema（输入 + 输出）
class OverallState(InputState, OutputState):
    pass

def answer_node(state: InputState):
    """处理节点： 根据question生成answer"""
    print(f"执行 answer_node 节点:")
    print(f"  输入: {state}")
    answer = "再见" if "bye" in state["question"].lower() else "你好"
    result = {"answer": answer, "question": state["question"]}
    print(f"输出：{result}")
    return result

def demo_input_output_schema():
    """演示：调用时只传 question，返回时只得到 answer。"""
    print("=== 演示输入输出模式 ===")

    # 指定 input_schema / output_schema，约束图的对外接口
    builder = StateGraph(
        OverallState, input_schema=InputState, output_schema=OutputState
    )
    builder.add_edge(START, "answer_node")
    builder.add_node("answer_node", answer_node)
    builder.add_edge("answer_node", END)
    graph = builder.compile()

    # invoke 只传 InputState 的字段；返回结果仅包含 OutputState 的字段
    result = graph.invoke({"question": "你好"})
    print(f"图调用结果: {result}")
    print(graph.get_graph().print_ascii())
    print()


def main():
    print("=== LangGraph 图输入输出模式===\n")
    demo_input_output_schema()
    print("=== 演示完成 ===")

if __name__ == "__main__":
    main()