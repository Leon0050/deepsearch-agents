# """
# 【案例】内存检查点 InMemorySaver：编译图时传入 checkpointer，用 thread_id 区分会话，演示 get_state / get_state_history / 二次 invoke。
#
# 对应教程章节：第 25 章 - LangGraph 高级特性 → 2、状态持久化（Persistence）
#
# 知识点速览：
# - compile(checkpointer=...) 后，每次 invoke 会在检查点中留下快照；config["configurable"]["thread_id"] 标识一条「对话线程」。
# - get_state(config) 取当前线程最新状态；get_state_history(config) 取历史快照序列（用于调试或时间回溯）。
# - `InMemorySaver` 数据仅在进程内存中，进程结束即丢失；它最适合先帮助你理解“checkpoint 到底是什么”。
# - 本例最值得观察的是：Persistence 不只是“把结果存起来”，而是把图每一步的状态历史都保留下来，为后面的 Time-Travel 打基础。
# """
#
#
# import operator
# from typing import Annotated, TypedDict
# from langgraph.graph import START,END, StateGraph
# from langgraph.checkpoint.memory import InMemorySaver
#
# class PersistenceDemoState(TypedDict):
#     # operator.add：列表/数值等按「相加」语义合并（列表相当于拼接）
#     messages: Annotated[list, operator.add]
#     step_count: Annotated[int, operator.add]
#
# def step_one(state: PersistenceDemoState) -> dict:
#     print("执行步骤 1")
#     return {
#         "messages": ["执行了步骤 1"],
#         "step_count": 1
#     }
#
#
# def step_two(state: PersistenceDemoState) -> dict:
#     print("执行步骤 2")
#     return {
#         "messages": ["执行了步骤 2"],
#         "step_count": 1,
#     }
#
#
# def step_three(state: PersistenceDemoState) -> dict:
#     print("执行步骤 3")
#     return {
#         "messages": ["执行了步骤 3"],
#         "step_count": 1,
#     }
#
#
# # def create_graph():
# #     builder = StateGraph(PersistenceDemoState)
# #
# #     builder.add_node("step_one", step_one)
# #     builder.add_node("step_two", step_two)
# #     builder.add_node("step_three", step_three)
# #
# #     builder.add_edge(START, "step_one")
# #     builder.add_edge("step_one", "step_two")
# #     builder.add_edge("step_two", "step_three")
# #     builder.add_edge("step_three", END)
#
#     return builder
#
# def create_graph():
#     builder = StateGraph(PersistenceDemoState)
#     builder.add_node("step_one", step_one).add_node("step_two", step_two).add_node("step_three", step_three)
#     builder.add_edge(START, "step_one").add_edge("step_one", "step_two").add_edge("step_two", "step_three").add_edge("step_three", END)
#     return builder
#
#
# def main():
#     print("=== LangGraph 1.0 内存持久化存储演示 ===\n")
#
#     graph = create_graph()
#     app= graph.compile(checkpointer=InMemorySaver())
#     config = {"configurable": {"thread_id" : "user_1381121"}}
#
#     # config = {"configurable": {"thread_id": "user_13811112222"}}
#
#     print("1. 首次执行工作流:")
#     # result = app.invoke(
#     #     {
#     #         "messages": ["开始执行"],
#     #         "step_count": 0,
#     #     },
#     #     config,
#     # )
#     result = app.invoke(
#         {"messages": ["开始执行步骤"],
#          "step_count": 0},
#         config,
#     )
#
#     print(f"执行结果 result: {result}\n")
#
#     print("2. 检查存储的状态:")
#     # saved_state = app.get_state(config)
#     saved_state = app.get_state(config)
#     print(f"保存的状态: {saved_state.values}")
#     print(f"下一个节点: {saved_state.next}\n")
#
#     # 正序遍历：从最早到最晚的检查点快照
#     # history = app.get_state_history(config)
#     history = app.get_state_history(config)
#     for checkpoint in history:
#         print("=" * 50)
#         print(f"当前状态: {checkpoint.values}")
#
#     print("=" * 80)
#     print("3. 恢复执行工作流:")
#     # 工作流若已结束，再次 invoke(None, config) 通常直接返回已落盘的结果
#     result2 = app.invoke(None, config)
#     print(f"恢复执行结果: {result2}\n")
#
#     print("=== 演示结束 ===")
#
#
# if __name__ == "__main__":
#     main()
#
# """
# 【输出示例】
# === LangGraph 1.0 内存持久化存储演示 ===
#
# 1. 首次执行工作流:
# 执行步骤 1
# 执行步骤 2
# 执行步骤 3
# 执行结果 result: {'messages': ['开始执行', '执行了步骤 1', '执行了步骤 2', '执行了步骤 3'], 'step_count': 3}
#
# 2. 检查存储的状态:
# 保存的状态: {'messages': ['开始执行', '执行了步骤 1', '执行了步骤 2', '执行了步骤 3'], 'step_count': 3}
# 下一个节点: ()
#
# ==================================================
# 当前状态: {'messages': ['开始执行', '执行了步骤 1', '执行了步骤 2', '执行了步骤 3'], 'step_count': 3}
# ==================================================
# 当前状态: {'messages': ['开始执行', '执行了步骤 1', '执行了步骤 2'], 'step_count': 2}
# ==================================================
# 当前状态: {'messages': ['开始执行', '执行了步骤 1'], 'step_count': 1}
# ==================================================
# 当前状态: {'messages': ['开始执行'], 'step_count': 0}
# ==================================================
# 当前状态: {'messages': [], 'step_count': 0}
# ================================================================================
# 3. 恢复执行工作流:
# 恢复执行结果: {'messages': ['开始执行', '执行了步骤 1', '执行了步骤 2', '执行了步骤 3'], 'step_count': 3}
#
# === 演示结束 ===
# """

"""
【案例】SQLite 检查点 SqliteSaver：把检查点写入本地 .db 文件，进程重启仍可恢复同 thread_id 的会话。

对应教程章节：第 25 章 - LangGraph 高级特性 → 2、状态持久化（Persistence）

知识点速览：
- 依赖包：项目根目录 `requirements.txt` 已包含 `langgraph-checkpoint-sqlite`；全量安装用 `pip install -r requirements.txt`，或单独 `pip install langgraph-checkpoint-sqlite`。生产环境更常用 Postgres（`langgraph-checkpoint-postgres`）等实现。
- SqliteSaver(conn=...) 与 sqlite3.connect 配合；数据库文件路径需本机可写，目录需事先存在。
- 与 InMemorySaver 用法相同：`compile(checkpointer=...)`、`invoke(..., config)`、`get_state(config)`，区别主要在于存储介质。
- 这个案例更像“从学习版持久化走向接近真实部署版”的过渡，重点是理解后端替换而不是 API 换了一套。
"""

import sqlite3
import operator
from pathlib import Path
from typing import Annotated, TypedDict

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, START, END

import sqlite3
import operator
from pathlib import Path
from typing import TypedDict, Annotated
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph,START,END


# class MyState(TypedDict):
    # messages: Annotated[list, operator.add]

class MyState(TypedDict):
    messages: Annotated[list, operator.add]

# def node_1(state: MyState):
#     return {"messages": ["abc", "def"]}

def node_1(state: MyState):
    return {"messages": ["abc", "def"]}

def main():
    # 默认写在项目旁，避免硬编码 Windows 盘符
    # db_dir = Path(__file__).resolve().parent / "sqlite_checkpoints"
    # db_dir.mkdir(parents=True, exist_ok=True)
    # db_path = db_dir / "sqlite_data.db"

    db_dir = Path(__file__).resolve().parent / "sqlite_checkpoints"
    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = db_dir / "sqlite_data.db"

    # conn = sqlite3.connect(database=str(db_path), check_same_thread=False)
    # sqlite_db = SqliteSaver(conn=conn)

    conn = sqlite3.connect(database=str(db_path), check_same_thread=False)
    sqlite_db = SqliteSaver(conn=conn)

    builder = StateGraph(MyState)
    builder.add_node("node_1", node_1).add_edge(START, "node_1").add_edge("node_1", END)
    graph = builder.compile(checkpointer=sqlite_db)

    # graph = builder.compile(checkpointer=sqlite_db)

    # 同一 thread_id 表示同一会话；多次执行会累积检查点，调试时可删 .db 或换 thread_id
    # config = {"configurable": {"thread_id": "user-001"}}
    config = {"configurable": {"thread_id": "user_001"}}

    initial_state = graph.get_state(config)
    # initial_state = graph.get_state(config)
    print(f"Initial state: {initial_state}")

    # result = graph.invoke({"messages": []}, config)
    result = graph.invoke({"messages":[]}, config)
    print(f"Result: {result}")

    print()
    print("====================查看执行后的状态====================")
    final_state = graph.get_state(config)
    print()
    print(f"Final state: {final_state}")

    conn.close()
    # conn.close()


if __name__ == "__main__":
    main()

"""
【输出示例】
Initial state: StateSnapshot(values={}, next=(), config={'configurable': {'thread_id': 'user-001'}}, metadata=None, created_at=None, parent_config=None, tasks=(), interrupts=())
Result: {'messages': ['abc', 'def']}

====================查看执行后的状态====================

Final state: StateSnapshot(values={'messages': ['abc', 'def']}, next=(), config={'configurable': {'thread_id': 'user-001', 'checkpoint_ns': '', 'checkpoint_id': '1f1272f0-d724-675e-8001-bb885d01bb16'}}, metadata={'source': 'loop', 'step': 1, 'parents': {}}, created_at='2026-03-24T03:10:46.773535+00:00', parent_config={'configurable': {'thread_id': 'user-001', 'checkpoint_ns': '', 'checkpoint_id': '1f1272f0-d723-6a48-8000-d3aac2954c9d'}}, tasks=(), interrupts=())
"""
