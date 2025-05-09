import logging
import uvicorn

from contextlib import asynccontextmanager
from fastapi import FastAPI

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from flight_search_app.agent import get_agent_async

from common.server.server import A2AServer
from common.server.task_manager import InMemoryTaskManager
from common.types import (
    SendTaskRequest,
    SendTaskResponse,
    Task,
    TaskStatus,
    Message,
    TextPart,
    TaskState,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger("flight_search_app.main")
agent_logger = logging.getLogger("flight_search_agent")
server_logger = logging.getLogger("flight_search_a2a_common_api")

class FlightAgentTaskManager(InMemoryTaskManager):
    def __init__(self, agent, runner, session_service):
        super().__init__()
        self.agent = agent
        self.runner = runner
        self.session_service = session_service
        logger.info("FlightAgentTaskManager initialized.")

    async def send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        task = Task(
            taskId=request.task.taskId,
            name="FlightSearch",
            inputs=request.task.inputs,
            outputs=request.task.outputs,
            status=TaskStatus.IN_PROGRESS,
            logs=[],
            artifacts=[]
        )
        logger.info(f"Processing task {task.taskId} for Flight Search")

        result = {
            "flight": f"Mock Flight to {request.task.inputs[0].value} on {request.task.inputs[1].value}",
            "price": "$199"
        }

        message = Message(parts=[TextPart(text=str(result))])
        task_state = TaskState(
            task=task,
            messages=[message],
            status=TaskStatus.COMPLETED,
        )

        return SendTaskResponse(state=task_state)

    def on_send_task(self, task):
        logger.info(f"Sending task: {task.taskId} with details: {task.inputs}")

    def on_send_task_subscribe(self, task):
        logger.info(f"Subscribing to task: {task.taskId}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    server_logger.info("Initializing Flight Search A2A Server...")

    agent_logger.info("Fetching ADK Agent...")
    agent = await get_agent_async()
    agent_logger.info("Successfully fetched ADK Agent.")

    session_service = InMemorySessionService()
    agent_logger.info("Created InMemorySessionService.")

    runner = Runner(agent=agent, session_service=session_service, app_name="FlightSearchApp")
    agent_logger.info("Created ADK Runner.")

    if hasattr(runner, "initialize") and callable(getattr(runner, "initialize")):
        try:
            agent_logger.info("Initializing ADK Runner...")
            await runner.initialize()
            agent_logger.info("Successfully initialized ADK Runner.")
        except Exception as e:
            agent_logger.warning(f"Runner initialization failed: {e}")
    else:
        agent_logger.warning("Runner does not have an initialize method. Skipping initialization.")

    task_manager = FlightAgentTaskManager(agent=agent, runner=runner, session_service=session_service)
    a2a_server = A2AServer(task_manager=task_manager)

    app.include_router(a2a_server.router)
    server_logger.info("A2A Server router registered.")

    if hasattr(runner, "router"):
        app.include_router(runner.router)
        server_logger.info("Runner router registered.")
    else:
        agent_logger.warning("Runner does not expose a router. Skipping router registration.")

    server_logger.info("Server startup complete.")
    yield
    server_logger.info("Server shutdown complete.")


app = FastAPI(lifespan=lifespan)

if __name__ == "__main__":
    server_logger.info("Starting Uvicorn server on 0.0.0.0:8000...")
    uvicorn.run("flight_search_app.main:app", host="0.0.0.0", port=8000, reload=True)