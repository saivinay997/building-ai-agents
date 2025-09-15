import io # for handling input/output operations
import json # for parsing JSON data
import os # for interacting with the operating system
import urllib3 # for making HTTP requests
import time # for time-related operations

import pdfplumber # for extracting text from PDF files
from dotenv import load_dotenv
from IPython.display import display, Markdown
from langchain_core.messages import BaseMessage, SystemMessage,ToolMessage, AIMessage
from langchain_core.tools import BaseTool, tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from typing import Annotated, ClassVar, Sequence, TypeDict, Optional

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()