# import json
# import os
# from dotenv import load_dotenv
# load_dotenv(encoding="utf-8")
# from typing import Annotated, List, TypedDict
# from langgraph.graph import StateGraph, START, END
# from langchain.chat_models import init_chat_model
# from langchain_core.messages import BaseMessage, HumanMessage, message_to_dict
# from langgraph.graph.message import add_messages
#
#
# # 1. 定义状态 State：messages 使用 add_messages 规约器，节点返回的每条新消息会自动追加到列表
#
#     # add_messages 是 LangGraph 提供的「规约器」（Reducer），来自 langgraph.graph.message。
#     # 含义：该字段不是「覆盖」更新，而是「追加」——节点只返回新增的消息（如 [reply]），
#     # 框架会把它们合并到当前消息列表末尾，适合多轮对话、多节点共同往同一列表写消息。
#     # 若不用 add_messages，节点返回 {"messages": [reply]} 会直接覆盖掉之前的对话历史。
#
#
# class DiliState(TypedDict):
#     messages: Annotated[List, add_messages]
#
# # 2. 初始化大模型（与第 10 章调用方式一致）
# llm = init_chat_model(
#     model="deepseek-chat",
#     model_provider="openai",
#     api_key=os.getenv("DEEPSEEK_API_KEY"),
#     base_url="https://api.deepseek.com/v1",
# )
#
#
# # 3. 定义节点 Nodes：将当前消息列表交给模型，返回新消息字典（add_messages 会追加到 state）
# def model_node(state: DiliState):
#     reply = llm.invoke(state["messages"])
#     return {"messages": [reply]}
#
# # 4. 构建图：单节点 model，START → model → END
# graph = StateGraph(DiliState)
# graph.add_node("model", model_node)
# graph.add_edge(START, "model")
# graph.add_edge("model", END)
#
# # 5. 编译并执行
# app = graph.compile()
# # 传入初始消息（HumanMessage 或字符串均可，视模型封装而定）
#
# result = app.invoke({"messages": [HumanMessage(content="请用一句话解释什么是 LangGraph。")]})
# # 或: result = app.invoke({"messages": "请用一句话解释什么是 LangGraph。"})
#
# print("模型回答：", result["messages"][-1].content)
#
# # 直接格式化输出 result：default 把消息对象转成 dict，其它不可序列化用 str 兜底
# print("\n--- result 格式化输出 ---")
# print(
#     json.dumps(
#         result,
#         ensure_ascii=False,
#         indent=2,
#         default=lambda o: message_to_dict(o) if isinstance(o, BaseMessage) else str(o),
#     )
# )
# # 可视化
#
# print(app.get_graph().print_ascii())
# print("=" * 50)
# print(app.get_graph().draw_mermaid())
# print("=" * 50)


from typing import TypedDict, Annotated
from langgraph.constants import START
from langgraph.graph import StateGraph, START, END

class QAState(TypedDict):
    query: str
    # rag_result: Annotated[str, add_messages]
    rag_result: str
    web_search_result: str
    final_answer:str


def rag_search_node(state: QAState):
    return {"rag_result": f"关于 {state['query']} 的知识库检索结果"}


def web_search_node(state: QAState):
    return {"web_search_result": f"关于 {state['query']} 的联网搜索结果"}


def final_answer_node(state: QAState):
    return {
        "final_answer": (
            f"基于知识库结果：{state['rag_result']}；"
            f"结合联网结果：{state['web_search_result']}；"
            "生成最终回答"
        )
    }

# builder = StateGraph(state_schema=QAState)
builder = StateGraph(QAState)
builder.add_node("rag_search_node", rag_search_node)
builder.add_node("web_search_node", web_search_node)
builder.add_node("final_answer_node", final_answer_node)

builder.add_edge(START, "rag_search_node")
builder.add_edge(START,"web_search_node")
builder.add_edge("rag_search_node", "final_answer_node")
builder.add_edge("web_search_node", "final_answer_node")
builder.add_edge("final_answer_node", END)

# graph = builder.compile()
app = builder.compile()
result = app.invoke({"query": "如何使用 LangGraph"})
print(result["final_answer"])
print(app.get_graph().print_ascii())

