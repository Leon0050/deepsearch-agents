# ========== 1. 导入与环境 ==========
import time
from langchain_openai import(ChatOpenAI,)
import os
from dotenv import load_dotenv
from langchain_core.exceptions import LangChainException
from pydantic import SecretStr

load_dotenv(encoding="utf-8")

import logging
_log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, _log_level, logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ========== 2. LLM 客户端初始化（封装为函数，便于多处复用） ==========

def init_llm_client() -> ChatOpenAI:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("Please configure DEEPSEEK_API_KEY")
    llm = ChatOpenAI(
        model="deepseek-chat",
        api_key=SecretStr(api_key),
        base_url="https://api.deepseek.com",
        temperature=0.7,
        max_tokens=2048,
    )
    return llm

def main():
    try:
        llm = init_llm_client()
        logger.info("LLM client initialized")
        # ----- 方式一：invoke（一次性拿完整回复） -----
        question="你是？"
        question2="介绍下langchain,三百字以内"
        response = llm.invoke(question)
        logger.info(f'问题：{question}')
        logger.info(f"回答：{response.content}")
        print("==================== 以下是流式输出")
        print("*" * 50)
        # ----- 方式二：stream（流式，边生成边输出） -----
        response_stream = llm.stream(question2)
        for chunk in response_stream:
            print(chunk.content, end="",flush=True)
            time.sleep(0.2)
        print()
    except ValueError as e:
        logger.error(f"配置错误：{str(e)}")
    except LangChainException as e:
        logger.error(f"模型调用失败：{str(e)}")
    except Exception as e:
        logger.error(f"未知错误：{str(e)}")

if __name__ == "__main__":
    main()