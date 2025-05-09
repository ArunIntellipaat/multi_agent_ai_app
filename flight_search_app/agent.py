import os
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

# --- ASYNC AGENT CREATION ---
async def get_agent_async():
    # Define MCP server parameters
    server_params = StdioServerParameters(
        command="mcp-flight-search",
        args=["--connection_type", "stdio"],
        env=None  # No environment variables needed
    )

    # Fetch tools from MCP server
    tools, exit_stack = await MCPToolset.from_server(connection_params=server_params)

    # Create the LLM agent using the fetched tools
    agent = LlmAgent(
        tools=tools,
        name="Flight_Search_Agent",
        description="Provides flight information based on user queries.",
        instruction="Use the tools to search for flights as per the user's request."
    )

    return agent

# --- MOCK MODE HANDLER ---
USE_MOCK = True

def handle_flight_task(task):
    if USE_MOCK:
        destination = task.get("destination", "Unknown")
        date = task.get("date", "Unknown Date")
        return {
            "flight": f"Mock Flight to {destination} on {date}",
            "price": "$199"
        }
    else:
        raise NotImplementedError("Real A2A flight agent not yet integrated with task execution.")