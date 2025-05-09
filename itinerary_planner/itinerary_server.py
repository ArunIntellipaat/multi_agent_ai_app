from fastapi import FastAPI, HTTPException
from itinerary_planner.itinerary_agent import ItineraryPlanner
from itinerary_planner.a2a.task_schema import TaskRequest  # Ensure this exists
import logging

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

# Instantiate the planner globally
planner = ItineraryPlanner()

@app.post("/v1/tasks/send")
async def send_task(request: TaskRequest):
    """Handle A2A tasks/send requests."""
    global planner

    if not planner:
        raise HTTPException(status_code=503, detail="Planner not initialized")

    try:
        task_id = request.taskId
        logging.debug(f"Received task request with taskId: {task_id}")

        # Log the incoming message
        user_message = None
        for part in request.message.parts:  # Access directly, no need for .get()
            if "text" in part.dict():  # Access the text from the Part object
                user_message = part.text
                break

        if not user_message:
            raise HTTPException(status_code=400, detail="No text message found in request")

        logging.debug(f"User message extracted: {user_message}")

        # Generate an itinerary based on the query
        itinerary = await planner.create_itinerary(user_message)

        logging.debug(f"Generated itinerary: {itinerary}")

        # Create the A2A response
        response = {
            "task": {
                "taskId": task_id,
                "state": "completed",
                "messages": [
                    {
                        "role": "user",
                        "parts": [{"text": user_message}]
                    },
                    {
                        "role": "agent",
                        "parts": [{"text": itinerary}]
                    }
                ],
                "artifacts": []
            }
        }

        return response

    except Exception as e:
        logging.error(f"Error while processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error while processing request: {str(e)}")

# Optional: Entry point for running directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("itinerary_planner.itinerary_server:app", host="0.0.0.0", port=8005, reload=True)