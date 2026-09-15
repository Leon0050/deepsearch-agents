from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, START, END
import operator
from langgraph.graph.message import add_messages

class Reducer(TypedDict):
    # 消息历史：add_messages 规约，新消息追加而非整表覆盖（与 StateReducer_AddMessages 一致可用 List）
    messages: Annotated[List, add_messages]
    # 标签列表：operator.add 将各节点返回的列表拼到已有列表后
    tags: Annotated[List[str], operator.add]
    # 累计分数：operator.add 做浮点数相加
    sore: Annotated[float, operator.add]

def process_user_message(state: Reducer) -> dict:
    # 获取最新消息；修复/注意：须用 .content 读正文（dict 入参在运行时已转为 HumanMessage 等对象，勿当普通 str 用）
    user_message = state["messages"][-1]
    return {
        # add_messages 会把本条 assistant 回复与历史合并
        "messages": [("assistant", f"Echo: {user_message.content}")],
        "tags": ["processed"],
        "score": 1.0,
    }


def add_sentiment_tag(state: Reducer) -> dict:
    # 本节点不写 messages，则 messages 仅由其他节点更新；tags/score 仍参与 operator.add 合并
    return {"tags": ["positive"], "score": 0.5}


def run_demo():
    builder = StateGraph(Reducer)
    builder.add_node("process", process_user_message)
    builder.add_node("sentiment", add_sentiment_tag)

    # 两节点都从 START 接入：并行分支，各自跑到 END
    builder.add_edge(START, "process")
    builder.add_edge(START, "sentiment")
    builder.add_edge("process", END)
    builder.add_edge("sentiment", END)

    graph = builder.compile()

    # invoke 只接收一个状态字典；messages 可用 dict 列表，与 Chat API 习惯一致
    result = graph.invoke(
        {
            "messages": [{"role": "user", "content": "Hello, how are you?"}],
            "tags": ["greeting"],
            "score": 0.0,
        }
    )
    print(result)

if __name__ == "__main__":
    run_demo()



    run_demo()


