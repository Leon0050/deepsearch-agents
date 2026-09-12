from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from dotenv import load_dotenv
import os
load_dotenv(encoding="utf-8")
API_KEY = os.getenv("DEEPSEEK_API_KEY")
from langchain.chat_models import init_chat_model

model = init_chat_model(
      model="deepseek-chat",
      model_provider="openai",
      api_key=API_KEY,
      base_url="https://api.deepseek.com",
      max_tokens=300,
      temperature=0.6,
)

# 方法1
template = PromptTemplate(
    template="你是个专业的{role}工程师，请回复{question}",
    input_variables=["role","questions"]
)
prompt = template.format(role="agent",questions="agent怎么创建？")

# 方法2 from_template
template = PromptTemplate.from_template("请给我一个关于{topic}的{type}解释")
prompt2 = template.format(topic="agent",type="怎么创建")

# example
template3 = PromptTemplate.from_template("请用一句话介绍{content}"
+ "内容不超过{length}个字"
)
prompt3 = template3.format(content="agent",length=50)
print(prompt3)

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

messages = [
    SystemMessage(content="你是一个Agent工程师"),
    HumanMessage(content="告诉我agent流程"),
    AIMessage(content="好的，我将告诉你详细流程")
]
###########
chat_prompt = ChatPromptTemplate.from_messages([
        ("system","你是一个{role}，请回答我提出的问题"),
        ("human", "请回答：{question}")
    ]
)

message = chat_prompt.format_messages(
    role="agent工程师",
    questions="agent怎么建造"
)
result = model.invoke(messages)

# 方式二：得到 ChatPromptValue
prompt_value = chat_prompt.invoke({
    "role": "python开发工程师",
    "question": "快速排序怎么写"
})                        
result = model.invoke(prompt_value)

# 方式三：得到纯字符串
prompt_str = chat_prompt.format(
    role="python开发工程师",
    question="快速排序怎么写"
)
print(prompt_str)
