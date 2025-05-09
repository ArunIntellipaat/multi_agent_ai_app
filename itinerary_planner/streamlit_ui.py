import streamlit as st
import requests
from datetime import datetime
import json

# API endpoint
API_URL = "http://localhost:8005/v1/tasks/send"

def log_user_query(query: str):
    """Log the user query."""
    with open("user_queries.log", "a") as f:
        f.write(f"{datetime.now()}: {query}\n")

def log_itinerary_request(payload: dict):
    """Log the payload sent to the API."""
    with open("requests.log", "a") as f:
        f.write(f"{datetime.now()} - Payload: {json.dumps(payload)}\n")

def generate_itinerary(query: str):
    """Send a query to the itinerary planner API."""
    try:
        task_id = "task-" + datetime.now().strftime("%Y%m%d%H%M%S")

        payload = {
            "taskId": task_id,
            "message": {
                "role": "user",
                "parts": [
                    {
                        "text": query
                    }
                ]
            }
        }

        # Log the query and request
        log_user_query(query)
        log_itinerary_request(payload)

        response = requests.post(API_URL, json=payload, headers={"Content-Type": "application/json"})
        response.raise_for_status()

        result = response.json()

        # Extract the agent's response
        for message in result.get("task", {}).get("messages", []):
            if message["role"] == "agent":
                for part in message["parts"]:
                    if "text" in part:
                        return part["text"]

        return "No response from itinerary planner agent."

    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit UI
st.title("🧳 AI-Powered Travel Itinerary Planner")

query = st.text_area("Enter your travel preferences or question:")

if st.button("Generate Itinerary"):
    if query.strip():
        with st.spinner("Planning your trip..."):
            result = generate_itinerary(query)
        st.success("Itinerary generated!")
        st.markdown(result)
    else:
        st.warning("Please enter a query to generate an itinerary.")