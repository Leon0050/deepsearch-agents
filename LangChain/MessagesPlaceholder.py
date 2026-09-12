from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


# 模板：系统消息 + 一个「消息占位符」memory + 当前用户问题 {question}
# memory 位置会在 invoke 时被替换成你传入的消息列表（如历史对话）
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是一个资深的Python应用开发工程师，请认真回答我提出的Python相关的问题",
        ),  # role 须为标准名：system / human / ai（不可自创如 system1）；也可写 SystemMessage(content="...")
        MessagesPlaceholder(
            "memory"
        ),  # 变量名可自取，如 "history"、"chat_history" 等，invoke 时键与之一致即可
        ("human", "{question}"),
    ]
)

# invoke 时传入：memory = 历史消息列表，question = 当前问题
# 这里用两条消息模拟「上一轮」的对话，再问「我的名字叫什么」来测试模型是否利用上下文
prompt_value = prompt.invoke(
    {
        "memory": [
            HumanMessage("我的名字叫亮仔，是一名程序员111"),
            AIMessage("好的，亮仔你好222"),
        ],
        "question": "请问我的名字叫什么？",
    }
)

# 把整段 prompt 转成字符串查看（系统设定 + 历史 + 当前问题）
print(prompt_value.to_string())

"""
【输出示例】
System: 你是一个资深的Python应用开发工程师，请认真回答我提出的Python相关的问题
Human: 我的名字叫亮仔，是一名程序员111
AI: 好的，亮仔你好222
Human: 请问我的名字叫什么？
"""

# 隐式：("placeholder", "{memory}") 等价于 MessagesPlaceholder("memory")
# 模板结构仍然建议写成「系统设定 + 历史消息 + 当前问题」，更便于和正文中的主线对应
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是一个资深的Python应用开发工程师，请认真回答我提出的Python相关的问题",
        ),
        ("placeholder", "{memory}"),
        ("human", "{question}"),
    ]
)

# 传入 memory（历史消息列表）和 question（当前问题）
prompt_value = prompt.invoke(
    {
        "memory": [
            HumanMessage("我的名字叫亮仔，是一名程序员"),
            AIMessage("好的，亮仔你好"),
        ],
        "question": "请问我的名字叫什么？",
    }
)
print(prompt_value.to_string())

"""
【输出示例】
System: 你是一个资深的Python应用开发工程师，请认真回答我提出的Python相关的问题
Human: 我的名字叫亮仔，是一名程序员
AI: 好的，亮仔你好
Human: 请问我的名字叫什么？
"""