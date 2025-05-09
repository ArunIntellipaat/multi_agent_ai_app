import os
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_mcp_adapters.client import MultiServerMCPClient

# MCP client configuration
MCP_CONFIG = {
    "hotel_search": {
        "command": "mcp-hotel-search",
        "args": ["--connection_type", "stdio"],
        "transport": "stdio",
        "env": {"SERP_API_KEY": os.getenv("SERP_API_KEY")},
    }
}

class HotelSearchAgent:
    """Hotel search agent using LangChain MCP adapters."""

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)

    def _create_prompt(self):
        """Create a prompt template with our custom system message."""
        system_message = "You are a helpful hotel search assistant."
        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

    async def process_query(self, query: str) -> str:
        """Process a user query asynchronously using the MCP adapter."""
        async with MultiServerMCPClient(MCP_CONFIG) as client:
            tools = client.get_tools()
            prompt = self._create_prompt()

            agent = create_openai_functions_agent(
                llm=self.llm,
                tools=tools,
                prompt=prompt
            )

            executor = AgentExecutor(
                agent=agent,
                tools=tools,
                verbose=True,
                handle_parsing_errors=True,
            )

            result = await executor.ainvoke({"input": query})
            return result["output"]

async def get_agent() -> HotelSearchAgent:
    return HotelSearchAgent()