import os
import logging
import uvicorn
from typing import Optional
from fastapi import FastAPI

from dotenv import load_dotenv
load_dotenv()

from hotel_search_app.langchain_agent import get_agent, HotelSearchAgent
from common.server.server import A2AServer
from common.server.task_manager import InMemoryTaskManager
from common.types import (
    AgentCard,
    SendTaskRequest,
    SendTaskResponse,
    Task,
    TaskStatus,
    Message,
    TextPart,
    TaskState,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class HotelAgentTaskManager(InMemoryTaskManager):
    """Task manager specific to the Hotel Search agent."""

    def __init__(self, agent: HotelSearchAgent):
        super().__init__()
        self.agent = agent
        logger.info("HotelAgentTaskManager initialized.")

    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        task = Task(
            id=request.task_id,
            name="HotelSearch",
            input=request.input,
            status=TaskStatus.IN_PROGRESS,
        )
        user_input = request.input.get("text", "")

        logger.info(f"HotelAgentTaskManager handling task {task.id} with input: {user_input}")

        try:
            response_text = await self.agent.process_query(user_input)
            message = Message(parts=[TextPart(text=response_text)])

            task_state = TaskState(
                task=task,
                messages=[message],
                status=TaskStatus.COMPLETED,
            )
            return SendTaskResponse(state=task_state)

        except Exception as e:
            logger.error(f"Error processing hotel search task: {e}")
            raise

    async def on_send_task_subscribe(self, request: SendTaskRequest) -> SendTaskResponse:
        # For now, you can implement this similarly or raise NotImplementedError
        raise NotImplementedError("Streaming task subscription is not implemented yet.")

async def run_server():
    logger.info("Starting Hotel Search A2A Server initialization...")

    agent_instance: Optional[HotelSearchAgent] = await get_agent()
    if not agent_instance:
        raise RuntimeError("Failed to initialize HotelSearchAgent")

    task_manager = HotelAgentTaskManager(agent=agent_instance)

    port = int(os.getenv("PORT", "8003"))
    host = os.getenv("HOST", "localhost")
    listen_host = "0.0.0.0"

    agent_card = AgentCard(
        name="Hotel Search Agent (A2A)",
        description="Provides hotel information based on location, dates, and guests.",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        capabilities={"streaming": False},
        skills=[
            {
                "id": "search_hotels",
                "name": "Search Hotels",
                "description": "Searches for hotels based on location, check-in/out dates, and number of guests.",
                "tags": ["hotels", "travel", "accommodation"],
                "examples": ["Find hotels in London from July 1st to July 5th for 2 adults"]
            }
        ]
    )

    a2a_server = A2AServer(
        agent_card=agent_card,
        task_manager=task_manager,
        host=listen_host,
        port=port
    )

    config = uvicorn.Config(app=a2a_server.app, host=listen_host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

# Only run if invoked directly
if __name__ == "__main__":
    import asyncio
    asyncio.run(run_server())