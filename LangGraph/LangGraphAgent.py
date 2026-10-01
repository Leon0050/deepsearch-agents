# """
# 【案例】单智能体最小闭环：create_agent 绑定 LLM 与工具，invoke 传入 messages，观察工具调用与最终回复。
#
# 对应教程章节：第 26 章 - LangGraph 多智能体与 A2A → 1、A2A 协议与多智能体架构概览
#
# 知识点速览：
# - 这是本章的“对照组”案例：先看单智能体已经能解决什么问题，再理解为什么某些场景并不需要一上来就拆成多智能体。
# - 单智能体：一个模型 + 一组工具，由模型决定何时调工具；适合单领域、小任务、统一入口的助手场景。
# - create_agent 返回的可执行对象底层仍基于 LangGraph；type(agent) 可帮助读者建立“高层 Agent 接口背后仍是图运行时”的认知。
# - 工具函数需清晰 docstring，便于模型理解参数与用途；本案例重点不是天气业务本身，而是“Agent + Tools”的最小闭环。
# - 注释中保留 stream 示例：stream_mode 可取 messages / updates / values / custom，用于和前面 LangGraph Streaming 主线衔接（需取消注释运行）。
# """
#
# import os
# from langchain.agents import create_agent
# from langchain.chat_models import init_chat_model
# from langchain_core.messages import HumanMessage
# from dotenv import load_dotenv
# load_dotenv(encoding="utf-8")
#
#
# def get_weather(city: str) -> str:
#     """获取指定城市的天气信息。
#
#     Args:
#         city: 城市名称
#     Returns:
#         返回该城市的天气描述（本案例为写死返回值，仅作演示）
#     """
#     return f"今天{city}是晴天，仅做测试，固定写死"
#
#
# def main():
#     # llm = init_chat_model(
#     #     model="qwen-plus",
#     #     model_provider="openai",
#     #     api_key=os.getenv("aliQwen-api"),
#     #     base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
#     # )
#
#     llm = init_chat_model(
#         model = "deepseek-chat",
#         model_provider = "openai",
#         api_key = os.getenv("DEEPSEEK_API_KEY"),
#         base_url = "https://api.deepseek.com"
#     )
#
#     # agent = create_agent(
#     #     model=llm,
#     #     tools=[get_weather],
#     # )
#
#     agent = create_agent(
#         model=llm,
#         tools=[get_weather],
#     )
#
#     print("agent 底层本质是个什么对象: " + str(type(agent)))
#     human_message= HumanMessage(content="今天深圳天气怎么样")
#     response = agent.invoke({"messages": [human_message]})
#
#     print()
#     print("模型回答：", response["messages"][-1].content)
#     print()
#     response["messages"][0].pretty_print()
#     response["messages"][-1].pretty_print()
#
#
#     # 流式示例（可选）：
#     # stream_mode：messages 流式 token；updates 每步工具；values 整状态快照；custom 配合 get_stream_writer
#     # for chunk in agent.stream(
#     #     {"messages": [{"role": "user", "content": "请问北京今天天气如何？"}]},
#     #     stream_mode="values",
#     # ):
#     #     chunk["messages"][-1].pretty_print()
#
#
# if __name__ == "__main__":
#     main()
#
# """
# 【输出示例】
# agent 底层本质是个什么对象: <class 'langgraph.graph.state.CompiledStateGraph'>
#
# 模型回答： 今天深圳是晴天。
#
# ================================== Ai Message ==================================
#
# 今天深圳是晴天。
# """


# """
# 【案例】Supervisor（推荐接口）：子 Agent 用 langchain.agents.create_agent，主管用 langgraph_supervisor.create_supervisor；交互式输入 + 流式输出 + 简单中文过滤。
#
# 对应教程章节：第 26 章 - LangGraph 多智能体与 A2A → 2、多智能体案例：Supervisor 与 Handoff
#
# 知识点速览：
# - 这是本章最重要的 Supervisor 案例：用 create_agent 定义子 Agent，再由 create_supervisor 统一调度，形成更贴近当前主流写法的多智能体结构。
# - 这里的“主管调子 Agent”本质上对应官方多智能体文档里的 Subagents 模式；主管负责统一入口与路由，子 Agent 负责狭窄领域任务。
# - pip install langgraph-supervisor；子 Agent 的工具函数必须具备清晰 docstring，便于模型绑定工具模式。
# - create_supervisor(...).compile() 得到可 stream/invoke 的图；主管 prompt 不只是提示词，更是在约束整个调度流程与角色边界。
# - filter_messages 只是教学辅助工具，用于弱化移交过程中的英文提示、去重和压缩噪声；重点应放在观察主管—子 Agent 的数据流与控制流。
# - 文末保留【输出示例】字符串，便于对照本地运行结果（模型输出可能略有差异）。
# """
#
# import os
# import re
#
# from langchain.agents import create_agent
# from langchain_openai import ChatOpenAI
# from langgraph_supervisor import create_supervisor
# from dotenv import load_dotenv
#
#
#
# import os
# import re
# from langchain.agents import create_agent
# from langgraph_supervisor import create_supervisor
# from langchain_openai import ChatOpenAI
# from dotenv import load_dotenv
# load_dotenv(encoding="utf-8")
# from pydantic import SecretStr
#
# # 1. 初始化大语言模型
# # def init_llm_model() -> ChatOpenAI:
# #     return ChatOpenAI(
# #         model="qwen-plus",
# #         api_key=os.getenv("aliQwen-api"),
# #         base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
# #         temperature=0.1,
# #         max_tokens=1024,
# #     )
#
# def init_llm_model() -> ChatOpenAI:
#
#     api_key = os.getenv("DEEPSEEK_API_KEY")
#     if api_key is None:
#         raise ValueError("no deepseek api key set")
#
#     return ChatOpenAI(
#         model="deepseek-chat",
#         api_key=SecretStr(api_key),
#         base_url="https://api.deepseek.com/",
#         temperature=0.1,
#         max_tokens=100
#     )
#
# # 2. Tools（必须有 docstring）
# def book_flight(from_airport: str, to_airport: str) -> str:
#     """预订航班工具。根据出发机场和到达机场预订一张机票，并返回预订结果。"""
#     return f"✅ 成功预订了从 {from_airport} 到 {to_airport} 的航班"
#
#
# def book_hotel(hotel_name: str) -> str:
#     """预订酒店工具。根据酒店名称完成酒店预订，并返回预订结果。"""
#     return f"✅ 成功预订了 {hotel_name} 的住宿"
#
#
# # 3. 子 Agent
#
# flight_assistant = create_agent(
#     model = init_llm_model(), tools=[book_flight], name="flight_assistant"
# )
#
# hotel_assistant =create_agent(
#     model=init_llm_model(), tools=[book_hotel], name="hotel_assistant"
# )
#
# # 4. 创建 Supervisor，协调者主管
# # supervisor = create_supervisor(
# #     agents=[flight_assistant, hotel_assistant],
# #     model=init_llm_model(),
# #     prompt=(
# #         "你是旅行预订系统的调度主管，负责协调航班预订和酒店预订。\n\n"
# #         "当用户提出航班和酒店预订请求时，你的工作流程是：\n"
# #         "1. 首先调用flight_assistant来预订航班\n"
# #         "2. 然后调用hotel_assistant来预订酒店\n"
# #         "3. 收到两个助手的结果后，汇总并向用户报告\n"
# #         "4. 完成后结束对话\n\n"
# #         "重要规则：\n"
# #         "- 每个助手只能调用一次\n"
# #         "- 不要重复任何内容\n"
# #         "- 不要输出任何英文\n"
# #         "- 所有通信都使用中文\n"
# #     ),
# # ).compile()
#
# supervisor = create_supervisor(
#     agents = [flight_assistant, hotel_assistant],
#     model = init_llm_model(),
#     prompt=(
#         "你是旅行预订系统的调度主管，负责协调航班预订和酒店预订。\n\n"
#         "当用户提出航班和酒店预订请求时，你的工作流程是：\n"
#         "1. 首先调用flight_assistant来预订航班\n"
#         "2. 然后调用hotel_assistant来预订酒店\n"
#         "3. 收到两个助手的结果完事后，汇总并向用户报告\n"
#         "4. 完成后结束对话\n\n"
#         "重要规则：\n"
#         "- 每个助手只能调用一次\n"
#         "- 不要重复任何内容\n"
#         "- 不要输出任何英文\n"
#         "- 所有通信都使用中文\n"
#     )
# ).compile()
#
#
# # 5. 消息过滤器：只服务于教学演示，帮助更清楚地观察主管和子 Agent 的有效中文输出
# def filter_messages(chunk: dict) -> str:
#     """提取并过滤消息，只返回中文内容，去除重复和英文"""
#     output = ""
#
#     if isinstance(chunk, dict):
#         for role, payload in chunk.items():
#             if isinstance(payload, dict) and "messages" in payload:
#                 for msg in payload["messages"]:
#                     if hasattr(msg, "content") and msg.content:
#                         content = msg.content.strip()
#
#                         # 过滤英文系统消息
#                         if (
#                             content
#                             and not content.startswith("Successfully")
#                             and not content.startswith("Transferring")
#                             and "Successfully transferred" not in content
#                             and "transferred back to" not in content
#                             and not content.startswith("帮我预订从")
#                         ):
#
#                             # 只保留中文内容
#                             chinese_content = re.sub(
#                                 r'[^\u4e00-\u9fff，。！？：；""、\s\d✅]', "", content
#                             )
#                             if chinese_content and len(chinese_content.strip()) > 5:
#                                 output += f"{role}: {chinese_content.strip()}\n"
#
#
#
# # 6. 主程序
# def main():
#     print("=" * 60)
#     print(
#         "智能旅行预订系统，由于大模型每次调用，可能出现预定不成功情况，这是正常反馈,主要是2026.2.8千问赠送奶茶活动，调用失败"
#     )
#     print("=" * 60)
#     print()
#
#     # 收集用户信息
#     print("请按顺序提供以下信息：")
#     print("-" * 40)
#
#     # 1. 询问出发机场
#     from_airport = input("1. 您的出发机场是哪里？: ").strip()
#     while not from_airport:
#         print("请输入有效的出发机场名称")
#         from_airport = input("1. 您的出发机场是哪里？: ").strip()
#
#     # 2. 询问到达机场
#     to_airport = input("\n2.您的到达机场是哪里？: ").strip()
#     while not to_airport:
#         print("请输入有效的到达机场名称")
#         to_airport = input("2. 您的到达机场是哪里？: ").strip()
#
#     # 3. 询问酒店名称
#     hotel_name = input("\n3. 您要预订的酒店名称是什么？: ").strip()
#     while not hotel_name:
#         print("请输入有效的酒店名称")
#         hotel_name = input("3. 您要预订的酒店名称是什么？: ").strip()
#
#     # 构造更明确的用户请求
#     user_request = (
#         f"请帮我预订以下旅行安排：\n"
#         f"1. 航班：从 {from_airport} 飞往 {to_airport}\n"
#         f"2. 酒店：{hotel_name}\n"
#         f"请完成这两个预订。"
#     )
#
#     print("\n" + "=" * 60)
#     print("正在处理您的预订请求...")
#     print("=" * 60)
#     print()
#
#     # 准备输入数据：Supervisor 图和普通 Agent 一样，入口仍然是 messages
#     input_data = {"messages": [{"role": "user", "content": user_request}]}
#
#     # 使用流式处理，便于观察主管如何依次调度两个子 Agent
#     try:
#         # 记录已打印内容，避免在演示时重复刷屏
#         seen_contents = set()
#
#         for chunk in supervisor.stream(input_data):
#             filtered_output = filter_messages(chunk)
#             if filtered_output:
#                 lines = filtered_output.strip().split("\n")
#                 for line in lines:
#                     if line and line not in seen_contents:
#                         print(line)
#                         seen_contents.add(line)
#
#         # 如果流式输出过少，就给一个兜底总结，避免读者误以为程序没有完成
#         if len(seen_contents) < 2:
#             print("\n" + "=" * 60)
#             print("预订已完成！")
#             print(f"航班：从 {from_airport} 到 {to_airport}")
#             print(f"酒店：{hotel_name}")
#             print("=" * 60)
#     except Exception as e:
#         print(f"\n处理过程中出现错误: {e}")
#         # 教学兜底：即使多智能体流程异常，也能直接调用工具帮助理解业务目标
#         print("\n正在直接执行预订...")
#         flight_result = book_flight(from_airport, to_airport)
#         hotel_result = book_hotel(hotel_name)
#         print(flight_result)
#         print(hotel_result)
#
#     print("\n感谢使用智能旅行预订系统！")
#
#
# # 7. 运行主程序
# if __name__ == "__main__":
#     try:
#         main()
#     except KeyboardInterrupt:
#         print("\n\n程序被用户中断。")
#     except Exception as e:
#         print(f"\n系统出现错误: {e}")
#
#
# """
# 【输出示例】
# ============================================================
# 智能旅行预订系统，由于大模型每次调用，可能出现预定不成功情况，这是正常反馈,主要是2026.2.8千问赠送奶茶活动，调用失败
# ============================================================
#
# 请按顺序提供以下信息：
# ----------------------------------------
# 1. 您的出发机场是哪里？: 北京
#
# 2. 您的到达机场是哪里？: 厦门
#
# 3. 您要预订的酒店名称是什么？: 厦门喜来登
#
# ============================================================
# 正在处理您的预订请求...
# ============================================================
#
# supervisor: 请帮我预订以下旅行安排：
# 1 航班：从 北京 飞往 厦门
# 2 酒店：厦门喜来登
# 请完成这两个预订。
# flight_assistant: 航班已成功预订！关于酒店预订厦门喜来登，当前工具不支持酒店预订功能。建议您通过酒店官网、旅行平台如携程、飞猪或联系酒店前台完成预订。如需其他帮助，请随时告诉我！
# supervisor: 航班已成功预订！关于酒店预订厦门喜来登，当前工具不支持酒店预订功能。建议您通过酒店官网、旅行平台如携程、飞猪或联系酒店前台完成预订。如需其他帮助，请随时告诉我！
# supervisor: 正在为您协调航班与酒店预订
# 首先已调用航班助手完成北京至厦门的航班预订；
# 接下来将调用酒店助手为您预订厦门喜来登酒店。
# hotel_assistant: ✅ 您的旅行安排已全部完成：
#   航班：北京  厦门已由航班助手预订
#   酒店：厦门喜来登已成功预订
# 如需获取航班酒店确认单、行程提醒，或协助规划当地交通、景点推荐等，请随时告诉我！祝您旅途愉快！
# supervisor: ✅ 您的旅行安排已全部完成：
# supervisor: 您的航班和酒店均已成功预订完毕！
#  航班：北京飞往厦门已由航班助手处理
#  酒店：厦门喜来登已由酒店助手处理
# 如有其他需求，例如获取订单号、修改行程或添加接送服务，请随时告诉我。祝您旅途顺利、愉快！
#
# 感谢使用智能旅行预订系统！
# """


"""
【案例】Handoff：用 Command + Send 把控制权与消息状态交给指定 Agent；create_task_description_handoff_tool 生成「移交」工具，子 Agent 可互相转接。

对应教程章节：第 26 章 - LangGraph 多智能体与 A2A → 2、多智能体案例：Supervisor 与 Handoff

知识点速览：
- Handoff 和 Supervisor 的最大区别，不是“也有多个 Agent”，而是“控制权会被正式交给下一位 Agent”，而不是始终由一个中央主管调度。
- Handoff 与“把子 Agent 当工具调”不同：这里显式构造下一跳输入 state，并用 Command(goto=[Send(...)], graph=Command.PARENT) 跳转到兄弟节点。
- InjectedState 把当前 MessagesState 注入工具，便于携带对话历史；task_description 充当“交给下一位的工单说明”，这正是 Handoff 里最值得关注的上下文工程。
- flight_assistant / hotel_assistant 由 create_agent 构建并作为节点加入同一 StateGraph，START 指向默认入口 Agent；这说明 Agent 完全可以作为 LangGraph 图中的节点来组织。
- @tool 装饰的业务工具仍需 docstring；本案例重点不是预订业务本身，而是观察“状态 + 任务说明 + 下一跳目标”如何一起交接。
"""

import os
from typing import Annotated

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START
from langgraph.graph.message import MessagesState
from langgraph.prebuilt.tool_node import InjectedState
from langgraph.types import Command, Send
from dotenv import load_dotenv

import os
from typing import Annotated
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START,END
from langgraph.graph.message import MessagesState
from langgraph.prebuilt.tool_node import InjectedState
from langgraph.types import Command, Send
from dotenv import load_dotenv
load_dotenv(encoding= "utf-8")
from pydantic import SecretStr

# ===============================
# 1. 初始化大语言模型
# ===============================
# def init_llm_model() -> ChatOpenAI:
#     return ChatOpenAI(
#         model="qwen-plus",
#         api_key=os.getenv("aliQwen-api"),
#         base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
#         temperature=0.1,
#         max_tokens=1024,
#     )

def init_llm_model() -> ChatOpenAI:


    api_key = os.getenv("DEEPSEEK_API_KEY")
    if api_key is None:
        raise ValueError("no key set")

    return ChatOpenAI(
        model = "deepseek-chat",
        api_key = SecretStr(api_key),
        base_url="https://api.deepseek.com",
        temperature=0.1,
        max_tokens= 1024
    )

# model = init_llm_model()
model = init_llm_model()


# ===============================
# 2. 通用 Handoff 工具工厂
# ===============================
def create_task_description_handoff_tool(
    *, agent_name: str, description: str | None = None
):
    name = f"transfer_to_{agent_name}"
    description = description or f"移交给 {agent_name}"

    # @tool(name, description=description)
    # def handoff_tool(
    #     task_description: Annotated[
    #         str, "描述下一个 Agent 应该做什么，包括所有必要信息"
    #     ],
    #     state: Annotated[MessagesState, InjectedState],
    # ) -> Command:

    @tool(name, description=description)
    def handoff_tool(
            task_description: Annotated[
                str, "描述下一个 Agent 应该做什么，包括所有必要信息"
            ],
            state: Annotated[MessagesState, InjectedState],
    ) -> Command:

        # task_description_message = {
        #     "role": "user",
        #     "content": task_description,
        # }
        # agent_input = {
        #     **state,
        #     "messages": [task_description_message],
        # }
        task_description_message = {
            "role": "user",
            "content" : task_description,
        }
        agent_input = {
            **state,
            "messages": [task_description_message],
        }

        # return Command(
        #     goto=[Send(agent_name, agent_input)],
        #     graph=Command.PARENT,
        # )

        return Command(
            goto=[Send(agent_name, agent_input)], # send agent_input to the agent(name)
            graph = Command.PARENT,
        )
    return handoff_tool
    return handoff_tool


# ===============================
# 3. 业务工具（必须有 docstring）
# ===============================
@tool("book_flight")
def book_flight(from_airport: str, to_airport: str) -> str:
    """预订航班，根据出发地和目的地完成机票预订"""
    print(f"✅ 成功预订了从 {from_airport} 到 {to_airport} 的航班")
    return f"成功预订了从 {from_airport} 到 {to_airport} 的航班。"


@tool("book_hotel")
def book_hotel(hotel_name: str) -> str:
    """预订酒店，根据酒店名称完成预订"""
    print(f"✅ 成功预订了 {hotel_name} 的住宿")
    return f"成功预订了 {hotel_name} 的住宿。"


# ===============================
# 4. Handoff 工具
# ===============================
transfer_to_flight_assistant = create_task_description_handoff_tool(
    agent_name="flight_assistant",
    description="将任务移交给航班预订助手",
)

transfer_to_hotel_assistant = create_task_description_handoff_tool(
    agent_name="hotel_assistant",
    description="将任务移交给酒店预订助手",
)


# ===============================
# 5. 定义 Agent（create_agent 新接口）
# 这里不额外写长 prompt，而是更多依赖：
# 1. 工具 schema / 名称 / docstring
# 2. Handoff 工具本身描述的交接语义
# 3. MessagesState 中持续携带的历史消息
# ===============================
# flight_assistant = create_agent(
#     model=model,
#     tools=[book_flight, transfer_to_hotel_assistant],  # 包含移交工具
#     name="flight_assistant",
# )
flight_assistant = create_agent(
    model = model,
    tools=[book_flight, transfer_to_hotel_assistant],
    name="flight_assistant",
)

hotel_assistant = create_agent(
    model=model,
    tools=[book_hotel, transfer_to_flight_assistant],  # 包含移交工具
    name="hotel_assistant",
)


# ===============================
# 6. 构建多 Agent Graph
# ===============================
# multi_agent_graph = (
#     StateGraph(MessagesState)
#     .add_node(flight_assistant)
#     .add_node(hotel_assistant)
#     .add_edge(START, "flight_assistant")
#     .compile()
# )

multi_agent_graph = (
    StateGraph(MessagesState).add_node(flight_assistant).add_node(hotel_assistant)
    .add_edge(START, "flight_assistant").compile()
)

# ===============================
# 7. 运行
# ===============================
if __name__ == "__main__":
    # result = multi_agent_graph.invoke(
    #     {
    #         "messages": [
    #             HumanMessage(content="帮我预订从北京到上海的航班，并预订如家酒店")
    #         ]
    #     }
    # )

    result = multi_agent_graph.invoke({"messages" :[
        HumanMessage(content = "帮我预订从北京到上海的航班，并预订如家酒店")
    ]})

    print("\n====== 最终对话结果 ======")
    for msg in result["messages"]:
        if msg.type in ("human", "ai"):
            # print(msg.content)
            msg.pretty_print()
"""
【输出示例】
✅ 成功预订了从 北京 到 上海 的航班
✅ 成功预订了 如家酒店 的住宿

====== 最终对话结果 ======
帮我预订从北京到上海的航班，并预订如家酒店
预订如家酒店

如家酒店已成功预订！如有其他需求，欢迎随时告知。
"""
