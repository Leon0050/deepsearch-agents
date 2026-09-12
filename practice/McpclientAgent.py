import asyncio
import os
import json
from pathlib import Path
from loguru import logger

# 默认 mcp.json 路径（与本文件同目录）
_MCP_JSON_PATH = Path(__file__).resolve().parent / "mcp.json"

def load_server(file_path: str | Path | None = None)-> dict:
    """
    加载 MCP 服务器配置。
    """
    path = Path(file_path) if file_path else _MCP_JSON_PATH
    if not path.exists():
        logger.warning(f"未找到 mcp 配置文件: {path}")
        return {"MCPSERVERS":{}}
    with open(path, "r", encoding="utf-8") as f:
        config = json.load(f)
    logger.info( f"已加载 mcp 配置: {path}，共 {len(config.get('mcpServers', {}))} 个服务")
    return config

async def run_chat_loop(config_path:str | Path| None = None) -> None:
    """
    启动并运行一个基于 MCP 工具的聊天 Agent 循环。
    """
    try :
        from langchain_mcp_adapters.client import MultiServerMCPClient
    except ImportError as e:
        logger.error( "请先安装 langchain-mcp-adapters: pip install langchain-mcp-adapters（部分环境需 Python 3.12 及以下）")
        raise e

    from langchain_openai import ChatOpenAI
    from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
    from langchain_core.prompts import ChatPromptTemplate, MessagePlaceholder

    config = load_server(config_path)
    servers = config.get("mcpServers", {})
    if not servers:
        logger.warning("mcp.json 中未配置任何服务，无法获取 MCP 工具")
        return

    # 初始化 MCP 客户端：connections 就是 mcp.json 中的 mcpServers 字典
    client = MultiServerMCPClient(connections=servers)

    tools = await client.get_tools()
    if not tools:
        logger.warning(  "未从 MCP 服务获取到任何工具，请确认服务已启动且 mcp.json 配置正确")
        return

    logger.info(f"已获取 {len(tools)} 个 MCP 工具: {[t.name for t in tools]}")

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if api_key is None:
        raise ValueError(f"no api key set")

    from pydantic import SecretStr

    llm = ChatOpenAI(
        model="deepseek-v4-flash",
        api_key=SecretStr(api_key),
        base_url="https://api.deepseek.com",
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "你是一个有用的助手，需要使用提供的工具来完成用户请求。"),
            ("human", "{input}"),
            MessagePlaceholder(variable_name="agent_scratchpad")
        ]
    )

    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent = agent,
        tools = tools,
        verbose = True,
        handle_parsing_errors = "解析用户请求失败，请重新输入清晰的指令",
    )
    logger.info("\n MCP Agent 已启动，请先输入一个提问给(LLM+MCP)，输入 'quit' 退出")

    while True:
        try:
            user_input = input("\n sir:").strip()
            if not user_input:
                continue
            if user_input.lower() == "quit":
                logger.info(f"exited")
                break
            result = agent_executor.invoke({"input", user_input})
            output = result.get("output", result)
            print(f"\nAgent: {output}")
        except KeyboardInterrupt:
            logger.info("exited")
            break

    def main() -> None:
        asyncio.run(run_chat_loop())

    if __name__ == "__main__":
        main()

