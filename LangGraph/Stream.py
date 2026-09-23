# # """
# # 【案例】流式传输图状态：对比 stream_mode 为 updates 与 values 时，每一步向调用方推送的内容差异。
# #
# # 对应教程章节：第 25 章 - LangGraph 高级特性 → 1、流式处理（Streaming）
# #
# # 知识点速览：
# # - `stream(..., stream_mode="updates")`：每步只推送“本节点本次改了什么”，更像增量日志。
# # - `stream(..., stream_mode="values")`：每步推送“当前完整状态长什么样”，更像全量快照。
# # - 这是理解第 25 章 Streaming 主线的关键案例：同一张图，只是换了流模式，看到的数据视角就完全不同。
# # """
# #
# # from typing import TypedDict
# # from langgraph.graph import StateGraph, START, END
# #
# #
# # class DiliState(TypedDict):
# #     topic: str
# #     joke: str
# #
# #
# # def refine_topic(state: DiliState):
# #     return {"topic": state["topic"] + " and cats"}
# #
# #
# # def generate_joke(state: DiliState):
# #     return {"joke": f"This is a joke about {state['topic']}"}
# #
# #
# # def main():
# #     graph = (StateGraph(DiliState)
# #              .add_node(refine_topic)
# #              .add_node(generate_joke)
# #              .add_edge(START, "refine_topic")
# #              .add_edge("refine_topic", "generate_joke")
# #              .add_edge("generate_joke", END)
# #              .compile()
# #     )
# #
# #     # updates：每步结束后只流出「本步对状态的更新」
# #     # for chunk in graph.stream({"topic": "ice cream"}, stream_mode="updates"):
# #         # print(chunk)
# #     for chunk in graph.stream({"topic": "ice cream"}, stream_mode="updates"):
# #         print(chunk)
# #
# #     print()
# #
# #     # values：每步结束后流出「当前完整 state」（未写字段可能仍为空字符串等初始形态）
# #     # for chunk in graph.stream({"topic": "ice cream"}, stream_mode="values"):
# #     for chunk in graph.stream({"topic": "ice cream"}, stream_mode = "values"):
# #         print(chunk)
# #
# #
# # if __name__ == "__main__":
# #     main()
# # """
# # 【输出示例】
# # {'refine_topic': {'topic': 'ice cream and cats'}}
# # {'generate_joke': {'joke': 'This is a joke about ice cream and cats'}}
# #
# # {'topic': 'ice cream'}
# # {'topic': 'ice cream and cats'}
# # {'topic': 'ice cream and cats', 'joke': 'This is a joke about ice cream and cats'}
# # """
#
# """
# 【案例】多模式流式传输：同一图依次演示 values、updates、列表组合 [values, updates]、以及 debug 模式。
#
# 对应教程章节：第 25 章 - LangGraph 高级特性 → 1、流式处理（Streaming）
#
# 知识点速览：
# - stream_mode 为列表时，每次迭代得到 (mode, chunk) 元组，便于前端按类型分别处理。
# - `values` 看“全貌”，`updates` 看“增量”；`debug` 输出更细，适合调试，不适合直接当业务输出。
# - 这个案例的核心价值是帮你建立“同一张图可以同时暴露多种观察视角”，而不是背住某个模式名。
# - 节点函数返回的字典仍按 State 的 Reducer 合并；本例字段未显式 Annotated，默认就是覆盖更新。
# """
#
# from typing import TypedDict
#
# from langgraph.graph import StateGraph, START, END
#
#
# class DiliState(TypedDict):
#     question: str
#     answer: str
#     confidence: float  # 置信度分数
#     steps: list
#
#
# def think(state: DiliState) -> DiliState:
#     """思考节点：模拟多步推理，写入 steps。"""
#     question = state["question"]
#     steps = [f"分析问题: {question}", "检索相关知识", "形成初步答案"]
#     return {"steps": steps}
#
#
# def respond(state: DiliState) -> DiliState:
#     """回应节点：根据关键词生成答案与置信度。"""
#     question = state["question"]
#     if "天气" in question:
#         answer = "今天天气晴朗"
#         confidence = 0.9
#     elif "时间" in question:
#         answer = "现在是上午10点"
#         confidence = 0.8
#     else:
#         answer = "这是一个很好的问题"
#         confidence = 0.7
#
#     return {
#         "answer": answer,
#         "confidence": confidence,
#     }
#
#
# def reflect(state: DiliState) -> DiliState:
#     """反思节点：在 steps 上追加校验与结论。"""
#     answer = state["answer"]
#     confidence = state["confidence"]
#     steps = state.get("steps", [])
#
#     steps.append(f"验证答案: {answer}")
#     steps.append(f"置信度评估: {confidence}")
#
#     if confidence > 0.8:
#         conclusion = "高置信度答案"
#     elif confidence > 0.5:
#         conclusion = "中等置信度答案"
#     else:
#         conclusion = "低置信度答案"
#
#     steps.append(f"结论: {conclusion}")
#
#     return {"steps": steps}
#
#
# def main():
#     builder = StateGraph(DiliState)
#     builder.add_node("think", think)
#     builder.add_node("respond", respond)
#     builder.add_node("reflect", reflect)
#
#     builder.add_edge(START, "think")
#     builder.add_edge("think", "respond")
#     builder.add_edge("respond", "reflect")
#     builder.add_edge("reflect", END)
#
#     graph = builder.compile()
#
#     print("=== LangGraph 多模式流式传输演示 ===\n")
#
#     input_state = {
#         "question": "今天天气怎么样?",
#         "answer": "",
#         "confidence": 0.0,
#         "steps": [],
#     }
#
#     print("--- 1. 使用 stream_mode='values' 模式 ---")
#     print("显示每一步执行后的完整状态:")
#     for chunk in graph.stream(input_state, stream_mode="values"):
#         print(f"  {chunk}")
#
#     print("\n" + "=" * 60 + "\n")
#
#     print("--- 2. 使用 stream_mode='updates' 模式 ---")
#     print("只显示每一步的状态更新:")
#     for chunk in graph.stream(input_state, stream_mode="updates"):
#         print(f"  {chunk}")
#
#     print("\n" + "=" * 60 + "\n")
#
#     print("--- 3. 同时使用 stream_mode=[values, updates] 多种流模式 ---")
#     print("同时显示完整状态和状态更新:")
#     for mode, chunk in graph.stream(input_state, stream_mode=["values", "updates"]):
#         print(f"  [{mode}]: {chunk}")
#
#     print("\n" + "=" * 60 + "\n")
#
#     print("--- 4. 使用 debug 模式 ---")
#     print("显示详细的调试信息:")
#     try:
#         for chunk in graph.stream(input_state, stream_mode="debug"):
#             print(f"  {chunk}")
#     except Exception as e:
#         print(f"  Debug模式可能需要特殊配置: {e}")
#
#
# if __name__ == "__main__":
#     main()


"""
【案例】messages 流模式：从图中调用 LLM 的节点逐 token（或片段）推送输出，便于打字机效果。

对应教程章节：第 25 章 - LangGraph 高级特性 → 1、流式处理（Streaming）

知识点速览：
- stream_mode="messages" 时，每次迭代一般为 (message_chunk, metadata)：chunk 为模型输出片段，metadata 标明节点等上下文。
- 这个案例最适合用来建立“LangGraph Streaming 不只流状态，也能流模型输出”这层认知。
- 流式消费侧通常关心 `chunk.content` 和 `metadata`；前者是输出片段，后者帮助你知道这些片段来自哪个节点。
- 需配置环境变量（如 aliQwen-api）与网络；模型、base_url 按你本地教程为准。
"""


# import os
# from typing import TypedDict
# from langchain.chat_models import init_chat_model
# from langgraph.graph import StateGraph, START
# from dotenv import load_dotenv
# from pydantic import SecretStr
#
# load_dotenv(encoding = "utf-8")
#
# class State(TypedDict):
#     query:str
#     answer:str
#
# api_key1 = os.getenv("DEEPSEEK_API_KEY")
# if api_key1 is None:
#     raise ValueError("API key is required")
#
# def node(state: State):
#     print("Let's call node.")
#     model = init_chat_model(
#         model="deepseek-chat",
#         model_provider="openai",
#         # api_key=SecretStr(api_key1)
#         api_key=api_key1,
#         base_url = "https://api.deepseek.com"
#     )
#
#     llm_result = model.invoke([("user", state["query"])])
#     print("llm invoke 结束", end="\n\n")
#     return {"answer": llm_result}
#
# def main():
#     graph = (
#         StateGraph(state_schema= State).add_node(node).add_edge(START, "node").compile()
#     )
#
#     inputs = {"query": "帮我生成一个200字的小学生作文，主题为我的一天"}
#
#     # messages：从图内触发的大模型调用处流式输出；(chunk, metadata) 见官方文档
#     # for chunk, _metadata in graph.stream(inputs, stream_mode="messages"):
#     #     # print(f"type of chunk:{type(chunk)}")  # 调试时可打开
#     #     print(chunk.content, end="")
#     #     # print(chunk, end="")
#     for chunk, _metadata in graph.stream(inputs, stream_mode="messages"):
#         print(chunk.content, end="")
#
# if __name__ == "__main__":
#     main()
# """
# 【输出示例】
# (.venv) didilili@DidililiMacBook-Pro streaming % python3 StreamLLMTokens.py
# 开始调用 node 节点
# 我的一天
#
# 清晨，阳光悄悄爬上窗台，我伸个懒腰起床了！吃完妈妈做的香喷喷的煎蛋和牛奶，背上书包去上学。课堂上，我认真听讲，积极举手回答问题；课间和好朋友跳皮筋、讲故事，笑声像铃铛一样清脆。中午吃食堂的番茄炒蛋盖饭，暖暖的真好吃！放学后，我先完成作业，再陪小猫“团团”玩一会儿毛线球。晚饭后，我和爸爸一起读绘本，妈妈教我折了一只纸鹤，翅膀还微微翘着呢！临睡前，我刷牙洗脸，把小书包整理好，明天还要早起升旗呢！这一天像一颗甜甜的水果糖——有学习的酸、玩耍的甜、家人的暖，还有成长的光。我爱这充实又快乐的一天！（198字）llm invoke 结束
# """

"""
【案例】自定义流（custom）最简版：在节点内通过 get_stream_writer() 写入任意可序列化数据，stream 侧用 custom 接收。

对应教程章节：第 25 章 - LangGraph 高级特性 → 1、流式处理（Streaming）

知识点速览：
- 这是 `custom` 模式的最小案例，重点不是业务逻辑，而是先看懂“节点内部怎么主动写出一段流式消息”。
- `get_stream_writer()` 仅在图执行（stream/astream）过程中有效；调用 `graph.stream` 时，`stream_mode` 里必须包含 `custom`。
- 自定义块与状态更新是分开的：前者更适合 UI/日志/进度提示，后者仍然通过 State 和 Reducer 管理。
"""

# from typing import TypedDict
#
# from langgraph.config import get_stream_writer
# from langgraph.graph import StateGraph, START, END
#
#
# class State(TypedDict):
#     query: str
#     answer: str
#
#
# def node(state: State):
#     writer = get_stream_writer()
#     writer({"custom_key": "欢迎来到线上Agent班级学习，O(∩_∩)O"})
#     return {"answer": "some data"}
#
#
# def main():
#     graph = (
#         StateGraph(State)
#         .add_node(node)
#         .add_edge(START, "node")
#         .add_edge("node", END)
#         .compile()
#     )
#
#     # for chunk in graph.stream({"query": "example"}, stream_mode=["custom"]): print(chunk)
#     # custom + updates：for mode, chunk in graph.stream(..., stream_mode=["updates", "custom"]): ...
#     for chunk in graph.stream({"query": "example"}, stream_mode=["values", "custom"]):
#         print(chunk)
#
#
# if __name__ == "__main__":
#     main()

"""
【输出示例】
('values', {'query': 'example'})
('custom', {'custom_key': '欢迎来到线上Agent班级学习，O(∩_∩)O'})
('values', {'query': 'example', 'answer': 'some data'})
"""
"""
【案例】自定义流 + 状态更新组合：节点内多次 writer(...) 推送进度，同时返回 dict 更新 State；演示 custom / updates / 组合。

对应教程章节：第 25 章 - LangGraph 高级特性 → 1、流式处理（Streaming）

知识点速览：
- `get_stream_writer()` 负责把“图运行过程中的自定义消息”主动往外推；它和节点返回的状态更新是两条并行通道。
- `stream_mode=["custom", "updates"]` 时，迭代得到 `(mode, chunk)`，非常适合前端一边看业务进度，一边看状态更新。
- 本例最值得观察的是：`writer(...)` 写出的 `custom` 数据不会自动进 State；节点真正写回图状态的，仍然是最后 return 的那份 dict。
"""


from typing import TypedDict
from langgraph.config import get_stream_writer
from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    query: str
    answer: str
    progress: list


def node_with_custom_streaming(state: State) -> State:
    """带自定义流式传输的节点：边写自定义流边更新状态。"""
    writer = get_stream_writer()
    writer({"custom_key": "开始处理查询"})
    writer({"progress": "步骤1: 分析查询内容", "status": "running"})

    query = state["query"]

    writer({"progress": "步骤2: 生成结果", "status": "running"})
    writer({"progress": "步骤3: 完成处理", "status": "completed"})
    writer({"custom_key": "查询处理完成"})

    result = f"处理结果: {query.upper()}"
    # return 用于更新state
    return {
        "answer": result,
        "progress": state.get("progress", []) + ["处理完成"],
    }


def main():
    print("=== LangGraph 自定义数据流式传输演示 ===\n")

    graph = (
        StateGraph(State)
        .add_node("node_with_custom_streaming", node_with_custom_streaming)
        .add_edge(START, "node_with_custom_streaming")
        .add_edge("node_with_custom_streaming", END)
        .compile()
    )

    inputs = {"query": "hello world", "answer": "", "progress": []}

    print("--- 1. 单独使用 custom 流模式 ---")
    try:
        for chunk in graph.stream(inputs, stream_mode="custom"):
            print(f"自定义数据块: {chunk}")
    except Exception as e:
        print(f"错误: {e}")
        print(
            "说明: 在 Graph API 中，自定义流数据需在节点中通过 get_stream_writer 发送"
        )

    print("\n" + "=" * 50 + "\n")

    print("--- 2. 单独使用 updates 流模式 ---")
    for chunk in graph.stream(inputs, stream_mode="updates"):
        print(f"状态更新: {chunk}")

    print("\n" + "=" * 50 + "\n")

    print("--- 3. 同时使用 custom 和 updates 流模式 ---")
    try:
        for mode, chunk in graph.stream(inputs, stream_mode=["custom", "updates"]):
            print(f"[{mode}]: {chunk}")
    except Exception as e:
        print(f"错误: {e}")
        print("说明: 请确认 LangGraph 版本支持多模式流")


if __name__ == "__main__":
    main()

"""
【输出示例】
=== LangGraph 自定义数据流式传输演示 ===

--- 1. 单独使用 custom 流模式 ---
自定义数据块: {'custom_key': '开始处理查询'}
自定义数据块: {'progress': '步骤1: 分析查询内容', 'status': 'running'}
自定义数据块: {'progress': '步骤2: 生成结果', 'status': 'running'}
自定义数据块: {'progress': '步骤3: 完成处理', 'status': 'completed'}
自定义数据块: {'custom_key': '查询处理完成'}

==================================================

--- 2. 单独使用 updates 流模式 ---
状态更新: {'node_with_custom_streaming': {'answer': '处理结果: HELLO WORLD', 'progress': ['处理完成']}}

==================================================

--- 3. 同时使用 custom 和 updates 流模式 ---
[custom]: {'custom_key': '开始处理查询'}
[custom]: {'progress': '步骤1: 分析查询内容', 'status': 'running'}
[custom]: {'progress': '步骤2: 生成结果', 'status': 'running'}
[custom]: {'progress': '步骤3: 完成处理', 'status': 'completed'}
[custom]: {'custom_key': '查询处理完成'}
[updates]: {'node_with_custom_streaming': {'answer': '处理结果: HELLO WORLD', 'progress': ['处理完成']}}
"""
