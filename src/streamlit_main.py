import streamlit as st
import json
import time
from typing import List, Dict, Any
from datetime import datetime
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import warnings
import logging

# Suppress ALTS and gRPC warnings from Google libraries
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GRPC_TRACE"] = ""

# Suppress specific warnings
warnings.filterwarnings("ignore", message=".*ALTS creds ignored.*")
warnings.filterwarnings("ignore", message=".*All log messages before absl::InitializeLog.*")

# Configure logging to suppress gRPC warnings
logging.getLogger("grpc").setLevel(logging.ERROR)
logging.getLogger("google").setLevel(logging.ERROR)

# Load environment variables
load_dotenv()

# Ensure local imports work when running Streamlit from project root
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

# Import the scientific research agent with error handling
try:
    from scientific_research_agent.workflow import run_research_workflow
    from langchain_core.messages import HumanMessage, AIMessage
    RESEARCH_AGENT_AVAILABLE = True
except ImportError as e:
    st.error(f"Error importing research agent: {str(e)}")
    st.error("Please check your package versions. Run: pip install -r requirements-fixed.txt")
    RESEARCH_AGENT_AVAILABLE = False
    run_research_workflow = None

# Page configuration
st.set_page_config(
    page_title="AI Agents Hub",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme styling
st.markdown("""
<style>
    /* Dark theme base */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #00d4aa;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .agent-card {
        background-color: #1e1e1e;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #00d4aa;
        color: #ffffff;
    }
    
    .agent-card h3 {
        color: #00d4aa;
    }
    
    .agent-card p, .agent-card li {
        color: #e0e0e0;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        max-width: 80%;
        color: #ffffff;
    }
    
    .user-message {
        background-color: #1a4d80;
        margin-left: auto;
        text-align: right;
        border: 1px solid #2d5a87;
    }
    
    .assistant-message {
        background-color: #2d2d2d;
        margin-right: auto;
        border: 1px solid #404040;
    }
    
    .template-query {
        background-color: #2a2a2a;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.3rem 0;
        cursor: pointer;
        border: 1px solid #00d4aa;
        transition: all 0.3s ease;
        color: #ffffff;
    }
    
    .template-query:hover {
        background-color: #3a3a3a;
        transform: translateY(-2px);
        border-color: #00f5d4;
    }
    
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-online {
        background-color: #00d4aa;
    }
    
    .status-offline {
        background-color: #ff6b6b;
    }
    
    /* Override Streamlit's default styling for dark theme */
    .stSelectbox > div > div {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    
    .stTextInput > div > div > input {
        background-color: #1e1e1e;
        color: #ffffff;
        border: 1px solid #404040;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #00d4aa;
        box-shadow: 0 0 0 1px #00d4aa;
    }
    
    .stButton > button {
        background-color: #00d4aa;
        color: #000000;
        border: none;
        border-radius: 5px;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background-color: #00f5d4;
        color: #000000;
    }
    
    /* Chat container styling */
    .stContainer {
        background-color: #0e1117;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #1e1e1e;
    }
    
    /* Info boxes */
    .stInfo {
        background-color: #1a4d80;
        border: 1px solid #2d5a87;
    }
    
    /* Error styling */
    .stError {
        background-color: #4a1a1a;
        border: 1px solid #6b2c2c;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_agent" not in st.session_state:
    st.session_state.selected_agent = "Scientific Research Agent"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}

# Available agents configuration
AGENTS_CONFIG = {
    "Scientific Research Agent": {
        "description": "Advanced AI agent for scientific research, paper analysis, and academic queries",
        "icon": "🔬",
        "status": "online",
        "capabilities": [
            "Search and analyze research papers",
            "Extract key insights from academic documents",
            "Provide detailed research summaries",
            "Answer scientific questions with citations"
        ]
    },
    "Data Analysis Agent": {
        "description": "Coming soon - AI agent for data analysis and visualization",
        "icon": "📊",
        "status": "offline",
        "capabilities": ["Data processing", "Statistical analysis", "Visualization"]
    },
    "Code Review Agent": {
        "description": "Coming soon - AI agent for code review and optimization",
        "icon": "💻",
        "status": "offline",
        "capabilities": ["Code analysis", "Bug detection", "Performance optimization"]
    }
}

# Template queries for the Scientific Research Agent
TEMPLATE_QUERIES = {
    "Scientific Research Agent": [
        "What are the latest developments in machine learning for drug discovery?",
        "Download and summarize the findings of this paper: https://arxiv.org/pdf/2509.12260",
        "What are the latest findings in neuroscience and brain-computer interfaces?",
        "Find research on sustainable agriculture practices",
        "What are the recent advances in artificial intelligence ethics?"
    ]
}

def get_agent_status_indicator(status):
    """Get HTML for agent status indicator"""
    status_class = "status-online" if status == "online" else "status-offline"
    return f'<span class="status-indicator {status_class}"></span>'

def display_agent_info(agent_name):
    """Display agent information card"""
    agent_info = AGENTS_CONFIG[agent_name]
    status_html = get_agent_status_indicator(agent_info["status"])
    
    st.markdown(f"""
    <div class="agent-card">
        <h3>{agent_info["icon"]} {agent_name}</h3>
        <p><strong>Status:</strong> {status_html}{agent_info["status"].title()}</p>
        <p><strong>Description:</strong> {agent_info["description"]}</p>
        <p><strong>Capabilities:</strong></p>
        <ul>
            {''.join([f'<li>{cap}</li>' for cap in agent_info["capabilities"]])}
        </ul>
    </div>
    """, unsafe_allow_html=True)

def display_template_queries(agent_name):
    """Display template queries for the selected agent"""
    if agent_name in TEMPLATE_QUERIES:
        st.subheader("🚀 Quick Start Templates")
        st.markdown("*Click on any template to use it as your query*")
        
        for i, query in enumerate(TEMPLATE_QUERIES[agent_name]):
            if st.button(query, key=f"template_{i}", help="Click to use this template"):
                st.session_state.user_input = query
                st.rerun()

def process_research_query(query: str) -> str:
    """Process query using the scientific research agent"""
    print("Processing research query:", query)
    if not RESEARCH_AGENT_AVAILABLE:
        return "The Scientific Research Agent is currently unavailable due to a compatibility issue. Please check your package versions and try again."
    
    try:
        # Use the wrapper function to run the research workflow
        result = run_research_workflow(query)
        print("Research agent result:", result)
        
        # Extract the final response
        if result and "messages" in result:
            # Get the last AI message
            for message in reversed(result["messages"]):
                # Include messages that do not contain tool calls or have empty tool_calls
                if isinstance(message, AIMessage) and not getattr(message, 'tool_calls', None):
                    return message.content
        
        # If no proper response found, try to extract any content
        if result and "messages" in result and result["messages"]:
            last_message = result["messages"][-1]
            if hasattr(last_message, 'content') and last_message.content:
                return last_message.content
        
        print("No AI message found in research agent result")
        return "I apologize, but I couldn't generate a proper response. Please try rephrasing your question."
    
    except Exception as e:
        st.error(f"Error processing query: {str(e)}")
        print("Error processing query:", e)
        import traceback
        traceback.print_exc()
        return "I encountered an error while processing your request. Please try again."

def display_chat_message(message: Dict[str, Any]):
    """Display a chat message with proper styling"""
    if message["role"] == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>You:</strong><br>
            {message["content"]}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <strong>🤖 {st.session_state.selected_agent}:</strong><br>
            {message["content"]}
        </div>
        """, unsafe_allow_html=True)

def main():
    # Main header
    st.markdown('<h1 class="main-header">🤖 AI Agents Hub</h1>', unsafe_allow_html=True)
    
    # Sidebar for agent selection
    with st.sidebar:
        st.header("🎯 Select Agent")
        
        # Agent selection
        selected_agent = st.selectbox(
            "Choose an AI Agent:",
            options=list(AGENTS_CONFIG.keys()),
            index=list(AGENTS_CONFIG.keys()).index(st.session_state.selected_agent)
        )
        
        # Update selected agent in session state
        if selected_agent != st.session_state.selected_agent:
            st.session_state.selected_agent = selected_agent
            # Clear messages when switching agents
            st.session_state.messages = []
        
        st.divider()
        
        # Display agent information
        display_agent_info(selected_agent)
        
        st.divider()
        
        # Display template queries
        display_template_queries(selected_agent)
        
        st.divider()
        
        # Chat controls
        st.subheader("💬 Chat Controls")
        
        if st.button("🗑️ Clear Chat History", help="Clear all chat messages"):
            st.session_state.messages = []
            st.rerun()
        
        # Display chat statistics
        if st.session_state.messages:
            st.metric("Messages", len(st.session_state.messages))
            st.metric("Agent", st.session_state.selected_agent)
    
    # Main chat interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(f"💬 Chat with {st.session_state.selected_agent}")
    
    with col2:
        if st.button("🔄 Refresh", help="Refresh the chat interface"):
            st.rerun()
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        if not st.session_state.messages:
            st.info("👋 Welcome! Select an agent and start chatting, or try one of the template queries from the sidebar.")
        else:
            for message in st.session_state.messages:
                display_chat_message(message)
    
    # Chat input
    st.markdown("---")
    
    # Check if user input is set from template query
    user_input = ""
    if "user_input" in st.session_state:
        user_input = st.session_state.user_input
        # del st.session_state.user_input
    
    # Chat input form
    with st.form("chat_form", clear_on_submit=False):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_query = st.text_input(
                "Type your message here...",
                value=user_input,
                placeholder=f"Ask {st.session_state.selected_agent} anything...",
                label_visibility="collapsed"
            )
        
        with col2:
            submit_button = st.form_submit_button("Send", use_container_width=True)
    
    # Process user input
    if submit_button and user_query:
        user_query = st.text_input(
                "Type your message here...",
                value=user_input,
                placeholder=f"Ask {st.session_state.selected_agent} anything...",
                label_visibility="collapsed"
            )
        # Add user message to chat history
        st.session_state.messages.append({
            "role": "user",
            "content": user_query,
            "timestamp": datetime.now().isoformat()
        })
        
        # Show typing indicator
        with st.spinner(f"{st.session_state.selected_agent} is thinking..."):
            # Process the query based on selected agent
            if st.session_state.selected_agent == "Scientific Research Agent":
                response = process_research_query(user_query)
            else:
                response = f"Sorry, the {st.session_state.selected_agent} is currently offline. Please select the Scientific Research Agent for now."
        
        # Add assistant response to chat history
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Clear the input field after successful submission
        st.session_state.user_input = ""
        
        # Rerun to display new messages
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; font-size: 0.8rem;'>
            🤖 AI Agents Hub | Built with Streamlit | Powered by LangGraph & Google Gemini
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
