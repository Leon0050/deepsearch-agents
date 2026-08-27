from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import os
load_dotenv(encoding="utf-8")
API_KEY = os.getenv("DEEPSEEK_API_KEY")

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