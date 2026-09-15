# from typing import List, Annotated, TypedDict, Dict, Any
# from langgraph.graph import StateGraph, START, END
# from langgraph.types import RetryPolicy
#
# # 定义状态类型
# class  DiliState(TypedDict):
#     result: str
#
# # 全局计数器：记录API尝试次数
# attempt_counter = 0
#
# # 工具函数
# def build_retry_graph(node_name: str, node_func, retry_policy: RetryPolicy):
#     builder= StateGraph(DiliState)
#     # 为节点添加重试策略，需要在add_node中设置retry_policy参数。
#     # retry_policy参数接受一个RetryPolicy命名元组对象。
#     # 默认情况下，retry_on参数使用default_retry_on函数，该函数会在遇到任何异常时重试
#     builder.add_node(node_name, node_func, retry_policy= retry_policy)
#     builder.add_edge(START, node_name)
#     builder.add_edge(node_name, END)
#     return builder.compile()
#
# # 模拟不稳定的API调用，使用全局变量跟踪尝试次数
# def unstable_api_call(state: DiliState) -> Dict[str, Any]:
#     """模拟不稳定API：前2次失败，第3次成功（全局计数器记录尝试次数）"""
#     global attempt_counter
#     attempt_counter += 1
#     # 纯文本打印尝试次数
#     print(f"尝试调用API，这是第 {attempt_counter} 次尝试")
#
#     # 模拟失败/成功逻辑：前2次抛异常，第3次返回结果
#     if attempt_counter < 3:
#         raise Exception(f"模拟API调用失败abcd (尝试 {attempt_counter})")
#     return {"result": f"API调用成功，经过 {attempt_counter} 次尝试"}
#
#
# # 自定义重试条件判断函数
# def custom_retry_on(exception: Exception) -> bool:
#     """自定义重试规则：只对包含「模拟API调用失败」的异常重试"""
#     print("########################:  " + str(exception))
#     err_msg = str(exception)
#     if "模拟API调用失败" in err_msg:
#         print(f"捕获到可重试异常: {err_msg}")
#         return True
#     print(f"捕获到不可重试异常: {err_msg}")
#     return False
#
#
# # 模拟抛出 ValueError 的节点
# def value_error_call(state: DiliState) -> Dict[str, Any]:
#     """模拟抛出ValueError：默认重试策略对这类异常不重试"""
#     print("调用会抛出 ValueError 的节点")
#     raise ValueError("模拟 ValueError 异常")
#
#
# # 测试方法1：默认重试策略
# def test_default_retry():
#     global attempt_counter
#     print("1. 使用默认重试策略:")
#     print("   默认策略会对除特定异常外的所有异常进行重试")
#     print("   不会重试的异常包括: ValueError, TypeError, ArithmeticError, ImportError,")
#     print("                     LookupError, NameError, SyntaxError, RuntimeError,")
#     print(
#         "                     ReferenceError, StopIteration, StopAsyncIteration, OSError\n"
#     )
#
#     print("测试默认重试策略:")
#     attempt_counter = 0  # 重置计数器
#     default_graph = build_retry_graph(
#         node_name="unstable_api",
#         node_func=unstable_api_call,
#         retry_policy = RetryPolicy(max_attempts=5),
#         # retry_policy=RetryPolicy(max_attempts=5),  # 最多5次尝试，足够重试成功
#     )
#     try:
#         result = default_graph.invoke({"result": ""})
#         print(f"最终结果: {result}\n")
#     except Exception as e:
#         print(f"最终失败: {type(e).__name__}: {e}\n")
#
#
# # 测试方法2：自定义重试策略（输出完全匹配要求）
# def test_custom_retry():
#     global attempt_counter
#     print("2. 使用自定义重试策略:")
#     print("   自定义策略只对特定错误进行重试\n")
#     print("测试自定义重试策略:")
#     attempt_counter = 0  # 重置计数器
#     custom_graph = build_retry_graph(
#         node_name="custom_retry_api",
#         node_func=unstable_api_call,
#         retry_policy = RetryPolicy(max_attempts=5, retry_on=custom_retry_on),
#         # retry_policy=RetryPolicy(max_attempts=5, retry_on=custom_retry_on),
#     )
#     try:
#         result = custom_graph.invoke({"result": ""})
#         print(f"最终结果: {result}\n")
#     except Exception as e:
#         print(f"最终失败: {type(e).__name__}: {e}\n")
#
#
# # 测试方法3：不可重试异常演示,测试 ValueError（默认策略不会重试）
# def test_no_retry_exception():
#     print("3. 测试不会重试的异常类型:")
#     print("测试 ValueError（默认策略不会重试）:")
#     no_retry_graph = build_retry_graph(
#         node_name="value_error_node",
#         node_func=value_error_call,
#         retry_policy=RetryPolicy(max_attempts=3),
#     )
#     try:
#         result = no_retry_graph.invoke({"result": ""})
#         print(f"最终结果: {result}\n")
#     except Exception as e:
#         print(f"最终失败: {type(e).__name__}: {e}\n")
#
#
# # 主演示函数
# def run_demo():
#     print("=== LangGraph 节点重试策略完整演示===")
#     print("-" * 80 + "\n")
#     # test_default_retry()
#     # test_custom_retry()
#     test_no_retry_exception()
#     print("-" * 80)
#     print("=== 演示结束 ===")
#
#
# # 程序入口
# if __name__ == "__main__":
#     run_demo()

from typing import Optional, TypedDict
from pydantic import BaseModel
from loguru import logger
from langgraph.graph import StateGraph, START, END


class MyState(BaseModel):
    """
       定义状态模型，用于在图节点之间传递数据
       Attributes:
           x (int): 输入的整数
           result (Optional[str]): 处理结果，可为"even"或"odd"
       """
    x:int
    result: Optional[str] = None

# 检查输入状态的节点函数
def check_x(state: MyState) -> MyState:
    """
    检查输入状态的节点函数
    Args:
        state (MyState): 包含输入数据的状态对象
    Returns:
        MyState: 返回原始状态对象，未做修改
    """
    logger.info(f"[check_x] Received state: {state}")
    return state


# 判断状态中x值是否为偶数的条件函数 #判断函数
def is_even(state: MyState) -> bool:
    """
    判断状态中x值是否为偶数的条件函数
    Args:
        state (MyState): 包含待判断数值的状态对象
    Returns:
        bool: 如果x是偶数返回True，否则返回False
    """
    return state.x % 2 == 0


# 处理偶数情况的节点函数
def handle_even(state: MyState) -> MyState:
    """
    处理偶数情况的节点函数
    Args:
        state (MyState): 包含偶数输入的状态对象
    Returns:
        MyState: 返回更新后的状态对象，result设置为"even"
    """
    logger.info("[handle_even] x 是偶数")
    return MyState(x=state.x, result="even")


# 处理奇数情况的节点函数
def handle_odd(state: MyState) -> MyState:
    """
    处理奇数情况的节点函数
    Args:
        state (MyState): 包含奇数输入的状态对象
    Returns:
        MyState: 返回更新后的状态对象，result设置为"odd"
    """
    logger.info("[handle_odd] x 是奇数")
    return MyState(x=state.x, result="odd")


builder = StateGraph(MyState)
# 添加节点
builder.add_node("check_x", check_x)
builder.add_node("handle_even", handle_even)
builder.add_node("handle_odd", handle_odd)

# 添加条件边，根据is_even函数的返回值决定流向哪个节点
# builder.add_conditional_edges(
#     "check_x", is_even, {True: "handle_even", False: "handle_odd"}
# )
builder.add_conditional_edges(
    "check_x", is_even, {True: "handle_even", False: "handle_odd"}
)

# 添加起始边，从START节点流向check_x节点
builder.add_edge(START, "check_x")

# 添加结束边，从处理节点流向END节点
builder.add_edge("handle_even", END)
builder.add_edge("handle_odd", END)

# 编译图结构
graph = builder.compile()

# 打印图的可视化结构
print(graph.get_graph().print_ascii())

# 测试用例：输入偶数4
logger.info("输入 x=4（偶数）")
graph.invoke(MyState(x=4))

# # 测试用例：输入奇数3
# logger.info("输入 x=3（奇数）")
# graph.invoke(MyState(x=3))

# builder1 = StateGraph(MyState)
# builder1.add_node("node_a", node_a)
# builder1.add_node("node_b", node_b)
# builder1.set_entry_point("node_a")
# builder1.add_edge("node_a", "node_b")
# builder1.set_finish_point("node_b")
# graph = builder1.compile()
# result = graph.invoke({})