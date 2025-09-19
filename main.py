import json
import dotenv
import os
import logging
import tempfile
import uuid
from typing import List, Dict, Any, Optional

from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from tavily import TavilyClient

dotenv.load_dotenv()

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

