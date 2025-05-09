# multi_agent_ai_app
This repo deals with deploying Multi-Agent AI App with Google’s A2A (Agent2Agent) Protocol, ADK, and MCP

Navigate to root directory and run the below command by opening separate WSL terminal

# Start Flight Search Agent - 1 Port 8000 
python3 -m flight_search_app.main

# Start Hotel Search Agent - 2 Port 8003
python3 -m hotel_search_app.langchain_server

# Start Itinerary Host Agent - Port 8005 
python3 -m itinerary_planner.itinerary_server

# Start frontend UI - Port 8501
streamlit run itinerary_planner/streamlit_ui.py