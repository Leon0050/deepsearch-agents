# """
# 【案例】子图作为节点：将 compile 后的子图直接 add_node 进父图；父子共用同一 State 类型时，由 Reducer 合并 messages。
#
# 对应教程章节：第 25 章 - LangGraph 高级特性 → 4、子图（Subgraphs）
#
# 知识点速览：
# - 这是子图最基础的入门案例：重点先理解“编译后的图也可以像节点一样被父图注册”。
# - 父子状态结构相同、且 `messages` 使用 add（列表拼接）时，本例会出现重复前缀，正好用来观察“父图和子图各自合并一次”带来的效果。
# - 这个案例不是在教“最佳消息合并策略”，而是在帮你建立对子图调用链和状态合并路径的第一直觉。
# """
#
# from operator import add
# from typing import Annotated, TypedDict, cast
# from langgraph.graph import START, END, StateGraph
#
# class DiliState(TypedDict):
#     """
#     状态：messages 使用 operator.add 合并策略——新返回的列表与原有列表拼接（非覆盖）。
#     """
#     messages: Annotated[list[str], add]
#
# def sub_node(state: DiliState) -> DiliState:
#     return {"messages": ["response from subgraph"]}
#
#
# # --- 子图 ---
# # subgraph_builder = StateGraph(DiliState)
# # subgraph_builder.add_node("sub_node", sub_node)
# # subgraph_builder.add_edge(START, "sub_node")
# # subgraph_builder.add_edge("sub_node", END)
# # subgraph = subgraph_builder.compile()
#
# subgraph = (StateGraph(DiliState).add_node("sub_node", sub_node)
#                     .add_edge(START, "sub_node").add_edge("sub_node", END).compile())
#
# # --- 父图：节点即子图 ---
# # builder = StateGraph(DiliState)
# # builder.add_node("subgraph_node", subgraph)
# # builder.add_edge(START, "subgraph_node")
# # builder.add_edge("subgraph_node", END)
#
# graph = (StateGraph(DiliState).add_node("subgraph_node", subgraph)
#            .add_edge(START, "subgraph_node").add_edge("subgraph_node", END).compile())
#
# # graph = builder.compile()
#
# """
# 子图调用的状态传递逻辑当主图调用子图节点时，整个过程会触发两次状态合并：
# 第一步：主图把初始状态 {"messages": ["main-graph"]} 传递给子图
#
# 第二步：子图内部执行 sub_node，返回 {"messages": ["response from subgraph"]}，
#         由于 add 策略，子图会把传入的 ["main-graph"] 和返回的 ["response from subgraph"] 拼接，
#         得到 ["main-graph", "response from subgraph"]
#
# 第三步：子图执行完成后，主图会再次应用 add 策略，
#     把主图原有的 ["main-graph"]
#     和子图返回的 ["main-graph", "response from subgraph"] 拼接，
#     最终得到 ["main-graph", "main-graph", "response from subgraph"]
# """
# print(graph.invoke({"messages": ["main-graph"]}))
# print()
# # 预期形态示例：{'messages': ['main-graph', 'main-graph', 'response from subgraph']}
#
# print(subgraph.get_graph().draw_mermaid())
# print("=" * 50)
# print()
#
# """
# 【输出示例】
# {'messages': ['main-graph', 'main-graph', 'response from subgraph']}
#
# ---
# config:
#   flowchart:
#     curve: linear
# ---
# graph TD;
#         __start__([<p>__start__</p>]):::first
#         sub_node(sub_node)
#         __end__([<p>__end__</p>]):::last
#         __start__ --> sub_node;
#         sub_node --> __end__;
#         classDef default fill:#f2f0ff,line-height:1.2
#         classDef first fill-opacity:0
#         classDef last fill:#bfb6fc
#
# ==================================================
# """

# """
# 【案例】父子图共享字段：父图 State 与子图 State 均含 parent_messages；子图内可改共享列表；子图私有字段不会出现在父图最终 state（父 schema 未声明）。
#
# 对应教程章节：第 25 章 - LangGraph 高级特性 → 4、子图（Subgraphs）
#
# 知识点速览：
# - 子图 compile 后作为父图的一个 node；父图 invoke 的初始状态会传入子图（字段对齐时）。
# - 子图 TypedDict 多出的键（如 sub_message）仅在子图内部可见，父图输出按 ParentState 过滤。
# - 本例重点是理解“父子图可以共享部分字段，但不是所有字段都会一路透到父图最终输出”。
# - 直接修改 `state["parent_messages"].append(...)` 时需注意：若追求更稳的不可变更新风格，真实项目里通常更推荐返回新列表；本例保留原地修改只是为了更容易观察共享字段变化。
# """
#
# from typing import TypedDict
# from langgraph.graph import StateGraph, START, END
#
#
# class ParentState(TypedDict):
#     parent_messages: list
#
#
# class SubgraphState(TypedDict):
#     parent_messages: list
#     sub_message: str
#
#
# def subgraph_node(state: SubgraphState) -> SubgraphState:
#     """子图节点：更新共享列表 + 写入子图私有字段。"""
#     state["parent_messages"].append("message from subgraph updateO(∩_∩)O")
#     state["sub_message"] = "subgraph private message"
#     return state
#
# def parent_node(state: ParentState) -> ParentState:
#     """父图首节点：保证 parent_messages 为列表并追加父侧消息。"""
#     if not state.get("parent_messages"):
#         state["parent_messages"] = []
#     state["parent_messages"].append("message from 父亲 node")
#     return state
#
#
# def build_subgraph():
#     """构建并返回编译后的子图。"""
#     sub_builder = StateGraph(SubgraphState)
#     sub_builder.add_node("sub_node", subgraph_node)
#     sub_builder.add_edge(START, "sub_node")
#     sub_builder.add_edge("sub_node", END)
#     return sub_builder.compile()
#
#
# def build_parent_graph(compiled_subgraph):
#     """构建并返回编译后的父图。"""
#     builder = StateGraph(ParentState)
#     builder.add_node("parent_node", parent_node)
#     builder.add_node("subgraph_node", compiled_subgraph)
#     builder.add_edge(START, "parent_node")
#     builder.add_edge("parent_node", "subgraph_node")
#     builder.add_edge("subgraph_node", END)
#     return builder.compile()
#
#
# def main():
#     # 构建子图
#     compiled_subgraph = build_subgraph()
#     # 构建父图
#     parent_graph = build_parent_graph(compiled_subgraph)
#     initial_state = {"parent_messages": ["我是父消息"]}
#     print("初始状态：", initial_state)
#
#     # 父图执行时会进入子图；sub_message 不会出现在父图最终 dict（ParentState 无此键）
#     final_state = parent_graph.invoke(initial_state)
#     print("\n执行后最终状态：", final_state)
#
#
# if __name__ == "__main__":
#     main()
# """
# 初始状态： {'parent_messages': ['我是父消息']}
#
# 执行后最终状态： {'parent_messages': ['我是父消息', 'message from 父亲 node', 'message from subgraph updateO(∩_∩)O']}
# """


"""
【案例】代理节点调用子图：父子 State 字段完全不同，不能直接把子图挂成节点；在父图节点里手动构造子图输入、invoke 子图、再把结果写回父 State。

对应教程章节：第 25 章 - LangGraph 高级特性 → 4、子图（Subgraphs）

知识点速览：
- 父状态 ParentState 专注业务（user_query / final_answer），子状态 SubgraphState 专注分析过程，二者无交集字段时必须「代理节点」做映射。
- 代理节点签名仍为 (父 state) -> 父 state 的增量/全量；内部调用 compiled_subgraph.invoke(subgraph_input)。
- 该模式可扩展任意形状的状态转换，是多智能体、流水线拆图时的常用技巧。
- 这个案例最值得读者记住的一句话是：父子图状态不一致时，不要硬凑，直接用“代理节点”做父→子、子→父的状态转换。

# 本例故意把父图状态和子图状态完全拆开，目的就是强调：真正复杂的子图集成，关键往往不在“怎么调用”，而在“怎么做状态转换”。
"""

from typing import TypedDict
from langgraph.graph import StateGraph, START, END


# 定义不同结构的父子图状态
# 父图状态：仅包含用户查询和最终答案（与子图状态完全不同）
class ParentState(TypedDict):
    user_query: str
    final_answer: str | None


# 子图状态：专注于分析逻辑（与父图状态无重叠字段）
class SubgraphState(TypedDict):
    analysis_input: str
    intermediate_steps: list
    analysis_result: str



# 定义子图核心逻辑
def subgraph_analysis_node(state: SubgraphState) -> SubgraphState:
    """子图核心节点：模拟分析流水线。"""
    query = state["analysis_input"]
    state["intermediate_steps"] = [f"解析查询：{query}", "执行分析逻辑", "生成结果"]
    state["analysis_result"] = f"针对「{query}」的分析结果：这是子图处理后的内容"
    return state


def build_subgraph() -> StateGraph:
    sub_builder = StateGraph(SubgraphState)
    sub_builder.add_node("subgraph_analysis_node", subgraph_analysis_node)
    sub_builder.add_edge(START, "subgraph_analysis_node")
    sub_builder.add_edge("subgraph_analysis_node", END)
    return sub_builder.compile()


compiled_subgraph = build_subgraph()


# 定义父图代理节点（核心：状态转换+调用子图）从节点调用图
def call_subgraph_proxy(state: ParentState) -> ParentState:
    """
    父图代理节点：
    1) 父 -> 子：拼子图输入；
    2) 调用子图 invoke；
    3) 子 -> 父：把 analysis_result 写入 final_answer。
    """
    subgraph_input = {
        "analysis_input": state["user_query"],
        "intermediate_steps": [],
        "analysis_result": "",
    }

    subgraph_response = compiled_subgraph.invoke(subgraph_input)

    return {
        "user_query": state["user_query"],
        "final_answer": subgraph_response["analysis_result"],
    }


def build_parent_graph():
    parent_builder = StateGraph(ParentState)
    # 添加代理节点（核心：手动处理状态转换+调用子图）
    parent_builder.add_node("call_subgraph_proxy", call_subgraph_proxy)
    # 父图执行链路：START → 代理节点 → END
    parent_builder.add_edge(START, "call_subgraph_proxy")
    parent_builder.add_edge("call_subgraph_proxy", END)
    return parent_builder.compile()


def main():
    # 1. 构建父图
    parent_graph = build_parent_graph()

    # 2. 定义父图初始状态（仅包含user_query，符合父图状态结构）
    initial_state = {
        "user_query": "请分析Python中StateGraph的使用场景",
        "final_answer": None,
    }
    print("父图初始状态：", initial_state)

    # 3. 执行父图，实际而言父图调用了call_subgraph_proxy
    final_state = parent_graph.invoke(initial_state)

    # 4. 输出结果
    print("\n父图最终状态：", final_state)
    print("\n子图处理后的最终答案：", final_state["final_answer"])


if __name__ == "__main__":
    main()

"""
【输出示例】
父图初始状态： {'user_query': '请分析Python中StateGraph的使用场景', 'final_answer': None}

父图最终状态： {'user_query': '请分析Python中StateGraph的使用场景', 'final_answer': '针对「请分析Python中StateGraph的使用场景」的分析结果：这是子图处理后的内容'}

子图处理后的最终答案： 针对「请分析Python中StateGraph的使用场景」的分析结果：这是子图处理后的内容
"""
