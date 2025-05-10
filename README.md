# multi_agent_ai_app
This repo deals with deploying Multi-Agent AI App with Google’s A2A (Agent2Agent) Protocol, ADK, and MCP

Navigate to root directory and run the below command by opening separate WSL terminal

# Run the below commands
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install fastapi uvicorn streamlit httpx python-dotenv pydantic
pip install google-generativeai google-adk langchain langchain-openai

# Install MCP Server Packages
pip install mcp-hotel-search
pip install mcp-flight-search
pip install langchain_mcp_adapters

# Configure Environment Variables
vi .env

# paste the below content
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key
SERP_API_KEY=your_serp_api_key

# Start Flight Search Agent - 1 Port 8000 
python3 -m flight_search_app.main

# Start Hotel Search Agent - 2 Port 8003
python3 -m hotel_search_app.langchain_server

# Start Itinerary Host Agent - Port 8005 
python3 -m itinerary_planner.itinerary_server

# Start frontend UI - Port 8501
streamlit run itinerary_planner/streamlit_ui.py