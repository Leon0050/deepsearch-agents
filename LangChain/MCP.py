# MCP Python SDK 2.x
import httpx
from mcp.server.mcpserver import MCPServer
import asyncio
from mcp import ClientSession ,StdioServerParameters
from mcp.client.stdio import stdio_client

server = MCPServer("Demo") # could set the necessary name

@server.tool() #注册工具
def add(a:int, b:int) -> int:
    return a+b

server.run()
# print(add(1,2))

server= MCPServer("123")
@ server.resource("greeting//deafult") #Client 可以读取：greeting://default 得到：Hello MCP 2.x
def get_greeting() -> str:
    return "Hello MCP 2.x"
server.run(transport="stdio")

@server.prompt()
def greet_user(name:str)-> str:
    return f"请给{name}写一段欢迎词"
server.run(transport="stdio")

async def main():
    server_params = StdioServerParameters(
        command = "python",
        args=["mcp_server_stdio.py"]
    )
    async with stdio_client(server_params) as (read,write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            result = await session.call_tool("add", {"a":1, "b":2})
            print(tools)
            print(result)
asyncio.run(main())

import json
import os
import httpx
from loguru import logger
from dotenv import load_dotenv
load_dotenv(encoding="utf-8")

# ---------------------- 极简版 MCP 服务类（无 FastMCP 依赖，纯手写）----------------------
class MCPWeatherServer:
    def __init__(self, name:str, host:str, port:int):
        self.name =  name
        self.host = host
        self.port = port
        self._tools = {}

    def tool(self):
        """实现 @server.tool() 装饰器：把普通函数登记到工具注册表中。"""
        def decorator(func):
            self._tools[func.__name__] = func # 注册工具函数，key 为函数名
            return func
        return decorator

    def run(self, transport:str):
        """模拟 run() 入口；这里只打印监听信息并保持进程存活，不提供完整网络服务。"""
        if transport == "sse":
            logger.warning(f"不支持的传输协议{transport}, 默认使用SSE")
        logger.info(f"启动 MCP SSE 天气服务器，监听 http://{self.host}:{self.port}/sse")
        self._keep_alive()

    def _keep_alive(self):
        """简单保持进程运行，便于从日志层面观察“服务端已启动”的状态。"""
        try:
            while True:
                pass
        except KeyboardInterrupt:
            logger.info("MCP 天气服务器已停止")

# ---------------------- 创建 MCP 实例并注册工具 ----------------------
# 对应教程：MCP 架构中的「MCP 服务器」角色，为客户端提供可暴露的能力

mcp = MCPWeatherServer("WeatherServerSSE", host="127.0.0.1", port=8000)

@server.tool()
def get_weather(city:str) -> str:
    """
    查询指定城市的即时天气信息。
    参数 city: 城市英文名，如 Beijing
    返回: OpenWeather API 的 JSON 字符串
    """
    url ="https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q":city,
        "appid": os.getenv("OPENWEATHER_API_KEY"),
        "units": "metrics",
        "lang": "zn_cn",
    }

    resp = httpx.get(url, params=params, timeout=10)
    data = resp.json()
    logger.info(f"查询:{city}天气结果:{data}")
    return json.dumps(data, ensure_ascii=False)

if __name__ == "__main__":
    logger.info(f"启动 MCP SSE 天气服务器，监听 http://127.0.0.1:8000/sse")
    server.run(transport = "sse")


import asyncio
import json
import os
from pathlib import Path
from loguru import logger
from pydantic import SecretStr
api_key = os.getenv("DEEPSEEK_API_KEY")

# 默认 mcp.json 路径（与本文件同目录）
_MCP_JSON_PATH = Path(__file__).resolve().parent / "mcp.json"

def load_servers(file_path : str | Path | None = None) -> dict:
    """
   加载 MCP 服务器配置。
   :param file_path: 配置文件路径，默认使用同目录下的 mcp.json
   :return: 完整配置字典，如 {"mcpServers": {"weather": {...}, "fetch": {...}}}

   这里读取的是“客户端如何连接服务”的约定配置，而不是协议本体。
   """
    path = Path(file_path) if file_path else _MCP_JSON_PATH
    if not path.exists():
        logger.info(f"未找到mcp配置文件:{path}")
        return {"mcpServers": {}}
    with open(path, "r", encoding="utf-8") as f:
        config = json.load(f)
        logger.info(
            f"已加载 mcp 配置: {path}，共 {len(config.get('mcpServers', {}))} 个服务"
        )
    return config

async def run_chat_loop(config_path: str | Path|None=None) -> None:
    """
   启动并运行一个基于 MCP 工具的聊天 Agent 循环。
   该函数会：1）加载 MCP 服务器配置；2）初始化 MCP 客户端并获取工具；
   3）创建基于 DeepSeek 的语言模型和 Agent；4）启动命令行聊天循环；5）退出时清理资源。
    """
    try:
        from langchain_mcp_adapters import MultiServerMCPClient
    except ImportError as e:
        logger.info(f"请先安装 langchain-mcp-adapters: pip install langchain-mcp-adapters（部分环境需 Python 3.12 及以下）")
        raise e
    from langchain_openai import ChatOpenAI
    from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain.chat_models import init_chat_model

    config = load_servers(config_path)
    servers = config.get("mcpServers",{})
    if not servers:
        logger.warning("mcp.json 中未配置任何服务，无法获取 MCP 工具")
        return

    # 初始化 MCP 客户端：connections 就是 mcp.json 中的 mcpServers 字典
    # 每个条目描述一台 MCP 服务该如何连接，例如 stdio 子进程或 HTTP/SSE 地址
    client = MultiServerMCPClient(connections=servers)

    # 按官方默认用法，MultiServerMCPClient 是无状态的；获取工具时使用异步接口即可
    tools = await client.get_tools()
    if not tools:
        logger.warning(
            "未从 MCP 服务获取到任何工具，请确认服务已启动且 mcp.json 配置正确"
        )
        return
    logger.info(f"已获取 {len(tools)} 个 MCP 工具: {[t.name for t in tools]}")

    llm = ChatOpenAI(
        model="deepseek-v4",
        api_key= SecretStr(api_key) if api_key else None,
        base_url="https://api.deepseek.com"
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "你是一个有用的助手，需要使用提供的工具来完成用户请求"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratched"),
        ]
    )

    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors="解析用户请求失败，请重新输入清晰的指令"
                                   )
    logger.info(f"\n MCP Agent已经启动，请先输入一个提问给(LLM+MCP)，输入 'quit' 退出")

    while True:
        try:
            user_input = input("\n您：").strip()
            if not user_input:
                continue
            if user_input.lower() == "quit":
                logger.info("已退出")
                break
            result= agent_executor.invoke({"input", user_input})
            output = result.get("output", result)
            print(f"\n Agent:{output}")
        except KeyboardInterrupt:
            logger.info(f"已退出")
            break


def main() -> None:
    asyncio.run(run_chat_loop())

if __name__ == "__main__":
    main()
