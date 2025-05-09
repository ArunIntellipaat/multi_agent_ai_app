import os
import logging
from fastapi import FastAPI
from itinerary_planner.itinerary_server import app
from uvicorn import run
from itertools import cycle

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Run the FastAPI server with uvicorn
def start_server():
    logger.info("Starting Itinerary Planner Server...")
    try:
        run(app, host="0.0.0.0", port=8005)
    except Exception as e:
        logger.error(f"Error starting the server: {str(e)}")

if __name__ == "__main__":
    start_server()