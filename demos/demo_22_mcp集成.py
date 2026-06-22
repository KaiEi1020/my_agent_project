# 💡 2026年伪代码示例：在 LangGraph 中集成标准 MCP Server
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langgraph.prebuilt import create_react_agent

# 1. 配置你想连接的 MCP Server（比如一个现成的 PostgreSQL 数据库 MCP 服务）
server_params = StdioServerParameters(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost:5432/audit_db"]
)

# 2. 启动并连接客户端
async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 💡 核心：直接从小工具服务器里拉取“标准定义好的工具”
            mcp_tools = await session.list_tools()
            
            # 3. 完美注入到你的 Agent 中
            # 无论是单兵 Agent 还是我们前面写的 Supervisor 旗下的 Worker，都能直接用！
            agent = create_react_agent(model, tools=mcp_tools)